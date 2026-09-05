<?php

use Illuminate\Support\Facades\Route;

// This app only renders Blade views — all the real logic (auth, admissions,
// courses, dashboards, file uploads, ...) lives in the Django REST API in
// backend/, called directly from the browser via portal.js/app.js. Routes
// here are extensionless (no more /about.html) since Blade has no reason
// to keep the old static-file naming.
Route::view('/', 'home');
Route::view('/about', 'about');
Route::view('/academics', 'academics');
Route::view('/student-life', 'student-life');
Route::view('/admissions', 'admissions');
Route::view('/news', 'news');
Route::view('/contact', 'contact');
Route::view('/application', 'application');
Route::view('/applicant-portal', 'applicant-portal');
Route::view('/student-portal', 'student-portal');
Route::view('/admissions-admin', 'admissions-admin');
Route::view('/dashboard-admin', 'dashboard-admin');
