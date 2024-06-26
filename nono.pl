:- use_module(library(clpfd)).

% ———————————————————————————————————————
%               GRID SETUP
% ———————————————————————————————————————
% main func
make_grid(Grid, RowLen, ColLen, Vars) :-
    length(Grid, RowLen),
    make_rows(Grid, ColLen, Vars).

% helper func to make rows
make_rows([], _, []).
make_rows([FirstRow|RestRows], Len, Vars) :-
    length(FirstRow, Len),
    make_rows(RestRows, Len, VarsRow),
    append(FirstRow, VarsRow, Vars).


% ———————————————————————————————————————
%                PRINTING
% ———————————————————————————————————————
% main func, calls all the prints 
print_grid(Rows, Cols, Grid) :-
    length(Cols, ColsLen),
    max_sublist_length(Rows, MaxRowLen),
    max_sublist_length(Cols, MaxColLen),
    pad_sublists(Rows, MaxRowLen, PaddedRows),
    pad_sublists(Cols, MaxColLen, PaddedCols),
    transpose(PaddedCols, TransposedCols),
    print_cols(TransposedCols, ColsLen, MaxRowLen),
    print_rows(PaddedRows, ColsLen, MaxRowLen, Grid).

% print each column (hints only)
print_cols([], ColsLen, MaxRowLen) :-
    print_separator(ColsLen, MaxRowLen).
print_cols([First|Rest], ColsLen, MaxRowLen) :-
    PaddingLen is MaxRowLen * 3 + 1,
    print_spaces(PaddingLen),
    write('| '),
    print_col_nums(First),
    nl,
    print_cols(Rest, ColsLen, MaxRowLen).

% helper for print_cols to print hints
print_col_nums([Last]) :-
    write(Last),
    write(' |').
print_col_nums([First|Rest]) :-
    atom_length(First, Length),
    (   Length == 2
    ->  write(First)
    ;   write(First),
        write(' ')
    ),
    (   Rest \= []
    ->  write('| ')
    ),
    print_col_nums(Rest).

% print each row (hints and values)
print_rows([], _, _, _).
print_rows([First|Rest], ColsLen, MaxRowLen, [FirstValues|RestValues]) :-
    print_row_nums(First),
    print_values(FirstValues),
    nl,
    DashesB is MaxRowLen * 3 + 1,
    print_dashes(DashesB),
    write('|'),
    print_spacers(ColsLen),
    nl,
    print_rows(Rest, ColsLen, MaxRowLen, RestValues).

% helper for print_rows to print hints
print_row_nums([Last]) :-
    atom_length(Last, Length),
    (   Length == 2
    ->  write(' '),
        write(Last)
    ;   write('  '),
        write(Last)
    ),
    write(' |').
print_row_nums([First|Rest]) :-
    atom_length(First, Length),
    (   Length == 2
    ->  write(' '),
        write(First)
    ;   write('  '),
        write(First)
    ),
    print_row_nums(Rest).

% print values
print_values([]).
print_values([First|Rest]) :-
    write(' '),
    (   First == 1
    ->  write('#')
    ;   write(' ')
    ),
    write(' |'),
    print_values(Rest).

% print separator between each row
print_separator(ColsLen, MaxRowLen) :-
    DashesLen is MaxRowLen * 3 + 1,
    print_dashes(DashesLen),
    write('|'),
    print_spacers(ColsLen),
    nl.

% helper for print_separator
print_spacers(1) :-
    write('\u2010\u2010\u2010|').
print_spacers(ColsLen) :-
    ColsLen > 0,
    write('\u2010\u2010\u2010|'),
    ColsLen1 is ColsLen - 1,
    print_spacers(ColsLen1).

% takes list of lists and returns list of padded sublists
pad_sublists([], _, []).
pad_sublists([Sublist|Rest], MaxColLen, [PaddedSublist|PaddedRest]) :-
    length(Sublist, SublistLen),
    PaddedLen is MaxColLen - SublistLen,
    pad_list(Sublist, PaddedLen, PaddedSublist),
    pad_sublists(Rest, MaxColLen, PaddedRest).

% ([1], 3, X) -> [' ', ' ', ' ', 1]
pad_list(List, 0, List).
pad_list(List, PaddingLength, PaddedList) :-
    PaddingLength > 0,
    PaddingLength1 is PaddingLength - 1,
    pad_list(List, PaddingLength1, Rest),
    PaddedList = [' ' | Rest].

% takes list of list and returns max sublist length
max_sublist_length([], 0).
max_sublist_length([Sublist|Rest], MaxLen) :-
    length(Sublist, SublistLen),
    max_sublist_length(Rest, RestMaxLen),
    MaxLen is max(SublistLen, RestMaxLen).

print_spaces(Length) :-
    length(SpacesList, Length),
    maplist(=(32), SpacesList),
    string_codes(Spaces, SpacesList),
    write(Spaces).

print_dashes(Length) :-
    length(DashesList, Length),
    maplist(=(8208), DashesList),
    string_codes(Dashes, DashesList),
    write(Dashes).


% ———————————————————————————————————————
%                 SOLVER
% ———————————————————————————————————————
% (solver Copyright (c) 2011 Lars Buitinck)
% % predicate to compare length of lists
% compare_length(>, L1, L2) :-
%     length(L1, Len1),
%     length(L2, Len2),
%     Len1 > Len2.
% compare_length(<, L1, L2) :-
%     length(L1, Len1),
%     length(L2, Len2),
%     Len1 < Len2.
% compare_length(=, _, _).

% % sort list by length
% sort_by_length(List, SortedList) :-
%     predsort(compare_length, List, SortedList).

% % sort hints and solve
% solve(RowSpec, ColSpec, Grid) :-
%     sort_by_length(RowSpec, SortedRowSpec),
%     sort_by_length(ColSpec, SortedColSpec),
%     rows(SortedRowSpec, Grid),
%     transpose(Grid, GridT),
%     rows(SortedColSpec, GridT).

solve(RowSpec, ColSpec, Grid) :-
    rows(RowSpec, Grid),
    transpose(Grid, GridT),
    rows(ColSpec, GridT).

rows([], []).
rows([C|Cs], [R|Rs]) :-
    row(C, R),
    rows(Cs, Rs).

row(Ks, Row) :-
    sum(Ks,  #=, Ones), % sum of the numbers given for the row
    sum(Row, #=, Ones), % count of the already filled in
    arcs(Ks, Arcs, start, Final),
    append(Row, [0], RowZ), % append 0 to end of Row, store list in RowZ
    % Sequence [0, 1, 1, 0, 0, etc.], Nodes [start, final], Arcs [arc of 0 to start, Arcs]
    automaton(RowZ, [source(start), sink(Final)], [arc(start,0,start) | Arcs]).

% Make list of transition arcs for finite-state constraint.
arcs([], [], Final, Final).
arcs([K|Ks], Arcs, CurState, Final) :-
    gensym(state, NextState), % generate unique symbol, "state[NextState]"
    (K == 0 ->
        % [x, y, z], if x has decreased to 0 then arc of 0 to CurState and arc of 0 to NextState
        % bind Rest to some internal variable
        Arcs = [arc(CurState,0,CurState), arc(CurState,0,NextState) | Rest],
        % Call arcs/4 with [y, z], Rest, NextState
        arcs(Ks, Rest, NextState, Final)
    ;
        % Color this state, create arc of 1 to NextState
        Arcs = [arc(CurState,1,NextState) | Rest],
        % Decrease count
        K1 #= K-1,
        % Calls arcs with same list but with decreased count
        arcs([K1|Ks], Rest, NextState, Final)
    ).

nono(Hints, SolvedGrid) :-
    Hints = [Rows, Cols],
    length(Rows, RowLen),
    length(Cols, ColLen),
    make_grid(Grid, RowLen, ColLen, Vars),
    % print_grid(Rows, Cols, Grid),
    % read(_),
    time(solve(Rows, Cols, Grid)),
    label(Vars),
    print_grid(Rows, Cols, Grid),
    SolvedGrid = Grid.

nono_timed(Hints, Time, SolvedGrid) :-
    Hints = [Rows, Cols],
    length(Rows, RowLen),
    length(Cols, ColLen),
    make_grid(Grid, RowLen, ColLen, Vars),
    % print_grid(Rows, Cols, Grid),
    % read(_),
    statistics(cputime, StartTime),
    solve(Rows, Cols, Grid),
    statistics(cputime, EndTime),
    Time is EndTime - StartTime,
    label(Vars),
    % print_grid(Rows, Cols, Grid),
    SolvedGrid = Grid.

