<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="api-base" content="http://localhost:8000/api">
<title>@yield('title', 'Anyschool High School')</title>
<link rel="stylesheet" href="/portal.css?v=35">
<script src="/portal.js?v=41" defer></script>
</head>
<body class="@yield('body_class')">
@yield('content')
</body>
</html>
