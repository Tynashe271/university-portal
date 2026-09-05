<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="api-base" content="http://localhost:8000/api">
<meta name="description" content="@yield('meta_description', 'Anyschool High School — learning with purpose, character and ambition.')">
<meta name="theme-color" content="#071c35">
<meta property="og:type" content="website">
<meta property="og:title" content="@yield('title', 'Anyschool High School')">
<meta property="og:description" content="@yield('meta_description', 'Learning with purpose, character and ambition.')">
<meta property="og:image" content="/og.png">
<meta name="twitter:card" content="summary_large_image">
<title>@yield('title', 'Anyschool High School')</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Libre+Franklin:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
<script src="/app.js" defer></script>
</head>
@php($page = trim($__env->yieldContent('body_page', 'home')))
<body data-page="{{ $page }}">
<a class="skip-link" href="#main">Skip to content</a>
@include('partials.header', ['page' => $page])
<main id="main">
@yield('content')
</main>
@include('partials.footer')
</body>
</html>
