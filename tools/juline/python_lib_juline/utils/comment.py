def format_comment(my_comment, center=False, frame=False):
    '''
    :param my_comment :type string ; EX: 'Je peux faire une liste :\n     > avec indentation\nPar exemple'
    :param center :type bool
    :param frame :type bool
    :return :type string
    # --------------------------- #
    #  Je peux faire une liste :  #
    #       > avec indentation    #
    #  Par exemple                #
    # --------------------------- #
    '''
    my_beautiful_comment = ''
    lines = []
    if '\n' in my_comment:
        for i in range(my_comment.count('\n') + 1):
            lines.append(len(my_comment.split('\n')[i]))
    if lines:
        lines.sort()
        max = lines[-1]
    else:
        max = len(my_comment)

    if max % 2 == 0:
        max = max + 2
    else:
        max = max + 3

    start_end = '# ' + ('-' * max) + ' #\n'
    empty_line = '# ' + (' ' * max) + ' #\n'

    if not center:
        for i in range(my_comment.count('\n') + 1):
            nb = max - len(my_comment.split('\n')[i])
            my_beautiful_comment = my_beautiful_comment + '#  ' + my_comment.split('\n')[i] + ' ' * nb + '#\n'
    else:
        for i in range(my_comment.count('\n') + 1):
            nb = (max - len(my_comment.split('\n')[i]))
            if nb == 2:
                my_beautiful_comment = my_beautiful_comment + '# ' + ' ' * (nb / 2) + my_comment.split('\n')[
                    i] + ' ' * (nb / 2) + ' #\n'
            elif nb % 2 != 0:
                my_beautiful_comment = my_beautiful_comment + '# ' + ' ' * (nb / 2) + my_comment.split('\n')[
                    i] + ' ' * (nb / 2) + '  #\n'
            elif nb % 2 == 0:
                my_beautiful_comment = my_beautiful_comment + '#' + ' ' * (nb / 2) + my_comment.split('\n')[
                    i] + ' ' * (nb / 2) + '#\n'

    if frame:
        my_beautiful_comment = start_end + empty_line + my_beautiful_comment + empty_line + start_end
    else:
        my_beautiful_comment = start_end + my_beautiful_comment + start_end

    print my_beautiful_comment