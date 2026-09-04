from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsAdminUser
from .models import QuestionBank, Assessment, Mark
from .serializers import QuestionBankSerializer, AssessmentSerializer, MarkSerializer

class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        classroom = self.request.query_params.get('classroom')
        subject = self.request.query_params.get('subject')
        if classroom:
            queryset = queryset.filter(classroom=classroom)
        if subject:
            queryset = queryset.filter(subject=subject)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Every mark for this assessment, ranked highest to lowest, with
        the class average — the "rankings" and "report" pieces of the
        Marks & Results module."""
        assessment = self.get_object()
        marks = assessment.marks.select_related('student').order_by('-score')
        rows = []
        for rank, mark in enumerate(marks, start=1):
            rows.append({
                'rank': rank,
                'student': mark.student_id,
                'student_name': f"{mark.student.first_name} {mark.student.last_name}".strip() or mark.student.username,
                'score': mark.score,
                'percentage': mark.percentage,
                'letter_grade': mark.letter_grade,
            })
        average = round(sum(float(r['score']) for r in rows) / len(rows), 1) if rows else None
        return Response({
            'assessment': AssessmentSerializer(assessment, context={'request': request}).data,
            'class_average': average,
            'rows': rows,
        })


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        assessment = self.request.query_params.get('assessment')
        student = self.request.query_params.get('student')
        if assessment:
            queryset = queryset.filter(assessment=assessment)
        if student:
            queryset = queryset.filter(student=student)
        return queryset

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(graded_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Enter a whole class's marks for one assessment in a single call:
        {"assessment": 4, "entries": [{"student": 5, "score": 78}, ...]}
        Updates an existing mark for that student/assessment rather than
        erroring on the unique_together, so corrections just resubmit.
        """
        assessment_id = request.data.get('assessment')
        entries = request.data.get('entries', [])
        if not assessment_id or not entries:
            return Response({'error': 'assessment and entries are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        saved, errors = [], []
        for entry in entries:
            student_id = entry.get('student')
            score = entry.get('score')
            if not student_id or score in (None, ''):
                continue
            try:
                score = float(score)
            except (TypeError, ValueError):
                errors.append(f"Student {student_id}: score must be a number.")
                continue
            if score > assessment.max_score:
                errors.append(f"Student {student_id}: score exceeds max ({assessment.max_score}).")
                continue
            mark, _created = Mark.objects.update_or_create(
                assessment=assessment,
                student_id=student_id,
                defaults={'score': score, 'comments': entry.get('comments', ''), 'graded_by': request.user},
            )
            saved.append(mark.id)
        return Response({'marked': len(saved), 'ids': saved, 'errors': errors}, status=status.HTTP_200_OK)