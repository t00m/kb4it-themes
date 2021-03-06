<!DOCTYPE Html>
<html lang="en">
<head>
    <title>KB4IT - ${var['title']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Asciidoctor 2.0.10">
    <meta name="description" content="KB4IT document">
    <meta name="author" content="KB4IT by t00mlabs.net">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="resources/themes/default/framework/uikit/css/uikit.min.css">
    <link rel="stylesheet" href="resources/themes/default/framework/uikit/css/coderay-asciidoctor.css">
    <link rel="stylesheet" href="resources/themes/default/framework/uikit/css/print.css" type="text/css" media="print" />
    <link rel="stylesheet" href="resources/themes/default/framework/uikit/uikit/css/kb4it.css">
    <script src="resources/themes/default/framework/uikit/js/uikit.min.js"></script>
    <script src="resources/themes/default/framework/uikit/js/uikit-icons.min.js"></script>
</head>
<body>
<div>
<div id="container-1" class="uk-container uk-container-center">
    <div id="kb4it-menu" style="z-index: 980;" uk-sticky="show-on-up: true">
        <nav class="uk-navbar-container uk-border-rounded uk-card-hover uk-margin" style="background-color: white;" uk-navbar>
            <div class="uk-navbar-left noprint">
                <ul class="uk-navbar-nav">
                    <li class="uk-link-toggle">
                        <a class="uk-logo uk-card uk-card-hover uk-border-rounded" href="index.html">
                            <img src="resources/themes/${var['theme']['id']}/images/logo.svg" alt="">
                        </a>
                    </li>
                    <li>
                        <a class="uk-button uk-card uk-card-hover uk-link-heading" href="#">Go To</a>
                        <div class="uk-navbar-dropdown">
                            <ul class="uk-nav uk-navbar-dropdown-nav">
                                <li class="uk-link-toggle">
                                    <a class="uk-card uk-card-hover uk-border-rounded uk-link-heading" href="dictionary.html"><span class="uk-padding-small">Dictionary</span></a>
                                </li>
                                <li class="uk-link-toggle">
                                    <a class="uk-card uk-card-hover uk-border-rounded uk-link-heading" href="topics.html"><span class="uk-padding-small">Topics</span></a>
                                </li>
                                <li class="uk-link-toggle">
                                    <a class="uk-card uk-card-hover uk-border-rounded uk-link-heading" href="pos.html"><span class="uk-padding-small">Part Of Speech</span></a>
                                </li>
                                <li class="uk-link-toggle">
                                    <a class="uk-card uk-card-hover uk-border-rounded uk-link-heading" href="grammar.html"><span class="uk-padding-small">Grammar</span></a>
                                </li>
                            </ul>
                        </div>
                    </li>
                </ul>
                <ul class="uk-navbar-nav">
                    <!-- MENU CONTENTS :: START -->
${var['menu_contents']}
                    <!-- MENU CONTENTS :: END -->
                </ul>
            </div>
