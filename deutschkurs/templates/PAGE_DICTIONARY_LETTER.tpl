= ${var['title']}

++++
<div class="uk-flex uk-flex-center">
    <ul class="uk-pagination" uk-margin>
    % for letter in var['letters']:
        <li class="uk-link-heading"><a href="dictionary-${letter}.html">${letter}</a></li>
    % endfor
    </ul>
</div>


<div class="uk-flex uk-flex-center">
    <ul class="js-filter uk-child-width-1-1 uk-width-1-1" uk-grid>
    <% letter_active = var['letter-active'] %>
    <li class="uk-margin-remove" data-letter="${letter}" data-size="large">
        <div class="uk-card uk-padding-remove uk-margin-remove uk-background-muted uk-text-left" uk-grid>
                        <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-width-1-4"><span class="uk-text-bold">Article</span></div>
                        <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-width-1-4"><span class="uk-text-bold">Word</span></div>
                        <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-width-1-4"><span class="uk-text-bold">Part Of Speech</span></div>
                        <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-width-1-4"><span class="uk-text-bold">Topic</span></div>
        </div>
    </li>
    % for word in var['dictionary'][letter_active]:
        <li class="uk-margin-remove" data-letter="${letter}" data-size="large">
            <div class="uk-card uk-card-body uk-padding-remove uk-margin-remove uk-card-hover uk-text-left" uk-grid>
                <%
                    try:
                        if var['cache']['words'][word]['article'] not in ['das', 'der', 'dia']:
                            article = ''
                        else:
                            article = var['cache']['words'][word]['article']
                    except:
                        article = ''
                %>

                <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-card-hover uk-width-1-4"><span class="uk-text-bold">${article}</span></div>
                <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-card-hover uk-width-1-4"><span class="uk-text-bold">${var['cache']['words'][word]['title']}</span></div>
                <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-card-hover uk-width-1-4"><span class="uk-text-primary">${var['cache']['words'][word]['part_of_speech']}</span></div>
                <%
                    topics = ' '.join(var['cache']['words'][word]['topic'])
                %>
                <div class="uk-card uk-card-body uk-padding-small uk-margin-remove uk-card-hover uk-width-1-4"><span class="uk-text-danger">${topics}</span></div>
            </div>
        </li>
        % endfor
    </ul>
</div>
++++
