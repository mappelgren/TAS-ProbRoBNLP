from ProbRobNLP import logic


def test_fill_gap_with_control():
    on = logic.Atom.from_string('on', 3, ['e1', 'X0', 'x1'])
    table = logic.Atom.from_string('table', 1, ['x0'])
    put = logic.Atom.from_string('put', 3, ['e0', 'X3', 'E0'])

    put_drs = logic.DRSish(put.terms, [put],
                          holes={'dobj': (put.terms[1], None),
                                 'prep': (put.terms[2], ('control', put.terms[1]))})

    table_drs = logic.DRSish(table.terms, [table])

    on_drs = logic.DRSish(on.terms, [on], holes={'control': (on.terms[1], None)})

    put_on = put_drs.fill_gap(on_drs, 'prep')
    put_on_table = put_on.fill_gap(table_drs, 'dobj')

    on2 = logic.Atom.from_string('on', 3, ['e1', 'x0', 'x1'])
    put2 = logic.Atom.from_string('put', 3, ['e0', 'x0', 'e1'])

    result_drs = logic.DRSish(list(set(on2.terms + put2.terms + table.terms)), [put2, on2, table])

    assert(result_drs == put_on_table)


def test_fill_gap_with_control2():
    on = logic.Atom.from_string('on', 3, ['e1', 'X0', 'x1'])
    table = logic.Atom.from_string('table', 1, ['x0'])
    put = logic.Atom.from_string('put', 3, ['e0', 'X3', 'E0'])

    put_drs = logic.DRSish(put.terms, [put],
                           holes={'dobj': (put.terms[1], None),
                                  'prep': (put.terms[2], ('control', put.terms[1]))})

    table_drs = logic.DRSish(table.terms, [table])

    on_drs = logic.DRSish(on.terms, [on], holes={'control': (on.terms[1], None)})

    put_table = put_drs.fill_gap(table_drs, 'dobj')
    put_on_table = put_table.fill_gap(on_drs, 'prep')

    on2 = logic.Atom.from_string('on', 3, ['e1', 'x0', 'x1'])
    put2 = logic.Atom.from_string('put', 3, ['e0', 'x0', 'e1'])

    result_drs = logic.DRSish(list(set(on2.terms + put2.terms + table.terms)), [put2, on2, table])

    assert (result_drs == put_on_table)

