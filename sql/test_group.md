An automatic judging system checks a solution for the task on multiple test cases. The outcome of a test case is binary: either the solution succeeds or fails. But not all test cases are eually important. Each test case is assigned to a group, and every test case in the group is worth the same number of points.
<br>

You have received a raw report with the results of the automatic testing. The report consists of two table, `test_groups` and `test_cases`, with the following structure:
<br>

    create table test_groups (
        name varchar(40) not null,
        test_value integer not null,
        unique(name)
    );
<br>

    create table test_cases (
        id integer not null,
        group_name varchar(40) not null,
        status varchar(5) not null,
        unique(id)
    );
<br>

Each row of the table `test_groups` contains information about a single group of tests: unique name (`name`) and the value of each test in the group (`test_value`). Each row of the table `test_cases` contains information about in single test case: unique id (`id`), the name of the group to which it belongs (`group_name`) and status (`status`). Status contains either one of two possible words: `OK` or `ERROR`
<br>

Write an SQL query that summarizes each group of tests. The table of results should contain four columns: `name` (name of the group), `all_test_cases` (number of tests in the group), `passed_test_cases` (number of test cases with the status `OK`), and `total_value` (total value of passed tests in this group). Rows should be ordered by decreasing `total_value`. In the case of a tie, rows should be sorted lexicographically be `name`.
<br>

Examples:
<br>

1. Given:
<br>
    test_groups:

        name                |   test_value
        --------------------+------------
        performance         |   15
        corner cases        |   10
        numerical stability |   20
        memory usage        |   10
    test_cases:
    
        id  | group_name            | status
        ----+-----------------------+-------------
        13  | memory usage          |   OK
        14  | numerical stability   |   OK
        15  | memory usage          |   ERROR
        16  | numerical stability   |   OK
        17  | numerical stability   |   OK
        18  | performance           |   ERROR
        19  | performance           |   ERROR
        20  | memory usage          |   OK
        21  | numerical stability   |   OK
<br>
Your query should return:

    name                | all_test_cases    | passed_test_cases | total_value
    --------------------+-------------------+-------------------+------------
    numerical stability |   4               |   4               |   80
    memory usage        |   3               |   2               |   20
    corner cases        |   0               |   0               |   0
    performance         |   2               |   0               |   0

2. Given:
<br>
    test_groups:

        name                    |   test_value
        ------------------------+------------
        performance             |   15
        corner cases            |   10
        numerical stability     |   20
        memory usage            |   10
        partial functionality   |   20
        full functionality      |   40
<br>
Your query should return:

    name                    | all_test_cases    | passed_test_cases | total_value
    ------------------------+-------------------+-------------------+------------
    corner cases            |   0               |   0               |   0
    full functionality      |   1               |   0               |   0
    memory usage            |   0               |   0               |   0
    numerical stability     |   0               |   0               |   0
    partial functionality   |   0               |   0               |   0
    performance             |   1               |   0               |   0
<br>

Assume that:
- Every `group_name` in the table `test_cases` also appears as `name` in the table `test_groups`.