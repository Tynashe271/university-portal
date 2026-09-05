@extends('layouts.site')

@section('title', "Contact | Anyschool High School")
@section('meta_description', "Contact Anyschool High School.")
@section('body_page', "contact")

@section('content')
<section class="page-hero"><div class="container"><p class="eyebrow">Contact us</p><h1>We’d love to hear from you.</h1><p>Ask about admissions, academics, visits or anything else you need.</p></div></section>
<section class="section contact contact-page"><div class="container contact-grid"><div><p class="eyebrow">Talk to us</p><h2>Start a conversation.</h2><p>Replace these placeholders with verified school details before publishing.</p><div class="contact-list"><a href="tel:+263000000000"><span>Call</span><strong>+263 00 000 0000</strong></a><a href="mailto:office@anyschool.example"><span>Email</span><strong>office@anyschool.example</strong></a><div><span>Visit</span><strong>School address, District, Zimbabwe</strong></div><div><span>Office hours</span><strong>Monday–Friday, 08:00–16:00</strong></div></div></div><form class="contact-form" id="contact-form"><div class="field-row"><label>Full name<input name="name" required></label><label>Email address<input name="email" type="email" required></label></div><label>How can we help?<select name="topic"><option>General enquiry</option><option>Admissions</option><option>Academics</option><option>School visit</option></select></label><label>Message<textarea name="message" rows="6" required></textarea></label><button class="btn btn-gold">Prepare email →</button><p class="form-note" id="contact-note"></p></form></div></section>
@endsection
