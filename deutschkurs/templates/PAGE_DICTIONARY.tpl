= ${var['title']}

++++
<div class="uk-flex uk-flex-center">
    <ul class="uk-pagination" uk-margin>
    % for letter in var['letters']:
        <li class="uk-link-heading"><a href="dictionary-${letter}.html">${letter}</a></li>
    % endfor
    </ul>
</div>
++++
