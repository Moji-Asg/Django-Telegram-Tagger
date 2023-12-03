$(() => {
    $('.loader').css('display', 'none');

    $('body').removeClass('no-animation');

    $('input[js-filter="double"]').on({
        'keypress': e=> {
            let text = $(e.target).val() + e.key;

            if (!onlyDouble(text) || !maximumFilter(text, 10) || !minimumFilter(text, 0, false)) {
                e.preventDefault();
            }
        }
    });

    $('textarea').on({
        'input': e => {
            $(e.target).css('height', 'auto');
            $(e.target).css('height', (e.target.scrollHeight + 4) + 'px');
        }
    });

    $('.reset-btn').on({
        'click': e => {
            e.target.blur();

            let targets = $('form input, form textarea, form select');

            for (let i=0;i<targets.length;i++) {
                let target = $(targets[i]);
                let value = target.attr('js-default');

                if (value === undefined) {
                    continue;
                }

                if (target.prop('type') === 'checkbox'){
                    if (value === 'True') {
                        target.prop('checked', true);
                    } else {
                        target.prop('checked', false);
                    }
                } else {
                    target.val(value);
                }
            }
        }
    });

    $('.theme-changer').on({
        'click': e => {
            e.target.blur();
            $('body').toggleClass('dark').toggleClass('light');
            $('.theme-changer i').toggleClass('fa-sun-bright').toggleClass('fa-moon');
        }
    });
})