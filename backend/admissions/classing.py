"""Automatic class placement for Form 1 applicants, based on the points
they scored (e.g. Grade 7 aggregate points) and how many seats are left
in each stream.

Points band -> starting stream:
    5  <= points < 10  -> stream 1  (class "1-1")
    10 <= points < 15  -> stream 2  (class "1-2")
    15 <= points < 25  -> stream 3  (class "1-3")
    25 <= points < 35  -> stream 4  (class "1-4")

Each class holds at most MAX_PER_CLASS students. If the student's own
stream is full, they overflow into the next stream up (1-1 -> 1-2 -> ...).
If every stream for the grade is already full, there is nowhere left to
place the student and the application is automatically declined.

Only Form 1 has a defined points scheme right now — it's the entry
point most schools stream by exam results. Other grades (Form 2-4,
Lower/Upper 6) are usually transfers without a comparable points system,
so they're placed manually and this module leaves them alone.
"""

MAX_PER_CLASS = 40

# (points >= lo, points < hi) -> stream number
POINTS_STREAM_BANDS = [
    (5, 10, 1),
    (10, 15, 2),
    (15, 25, 3),
    (25, 35, 4),
]
MIN_POINTS = POINTS_STREAM_BANDS[0][0]
MAX_POINTS = POINTS_STREAM_BANDS[-1][1]
MAX_STREAM = max(stream for _lo, _hi, stream in POINTS_STREAM_BANDS)

# Grades with a defined points -> class scheme. Extend this (and the grade
# prefix used in the class name) if other grades get their own scheme.
STREAMED_GRADES = {'form1': '1'}


def stream_for_points(points):
    for lo, hi, stream in POINTS_STREAM_BANDS:
        if lo <= points < hi:
            return stream
    return None


def assign_class(application, points):
    """Pick a class for `application` given `points`.

    Returns (class_name, outcome) where outcome is one of:
      'placed'       - class_name is where the student was placed
      'out_of_range' - points fall outside every defined band (a data
                        entry problem, not a capacity one)
      'full'         - every stream for this grade is at capacity
      'unstreamed'   - this grade has no defined points scheme
    """
    grade_prefix = STREAMED_GRADES.get(application.grade_applying_for)
    if grade_prefix is None:
        return None, 'unstreamed'

    stream = stream_for_points(points)
    if stream is None:
        return None, 'out_of_range'

    from .models import AdmissionApplication

    for s in range(stream, MAX_STREAM + 1):
        class_name = f"{grade_prefix}-{s}"
        count = AdmissionApplication.objects.filter(
            grade_applying_for=application.grade_applying_for,
            academic_year=application.academic_year,
            assigned_class=class_name,
            status__in=['approved', 'admitted', 'enrolled'],
        ).exclude(pk=application.pk).count()
        if count < MAX_PER_CLASS:
            return class_name, 'placed'

    return None, 'full'
