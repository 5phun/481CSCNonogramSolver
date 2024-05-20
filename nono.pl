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
    write('\u2014\u2014\u2014|').
print_spacers(ColsLen) :-
    ColsLen > 0,
    write('\u2014\u2014\u2014|'),
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
    maplist(=(8212), DashesList),
    string_codes(Dashes, DashesList),
    write(Dashes).


% ———————————————————————————————————————
%                 SOLVER
% ———————————————————————————————————————
% TODO
solve(Rows, Cols, Grid).


% ———————————————————————————————————————
%                 EXAMPLES
% ———————————————————————————————————————
example1([[2], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]],
         [[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]]).
example1 :-
    example1(Rows, Cols),
    length(Rows, RowLen),
    length(Cols, ColLen),
    make_grid(Grid, RowLen, ColLen, Vars),
    print_grid(Rows, Cols, Grid),
    read(_),
    solve(Rows, Cols, Grid),
    label(Vars),
    print_grid(Rows, Cols, Grid).
