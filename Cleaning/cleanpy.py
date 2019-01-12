# -*- coding: utf-8 -*-

import numpy as np

def chopseries( s , search = 'end', nuq_min = 1, nuq_max = 5, thres = 0.3, char_min = 4):

    # =========================================================================
    #     Function: chopseries( s , search = 'end', nuq_min = 1, nuq_max = 5,
    #                           thres = 0.25, char_min = 4)
    #
    #               s: Pandas Series
    #               search: Specify if the pattern search beings at the
    #                       start or end of the string
    #               nuq_min: Min specified # of unique values
    #               nuq_max: Max specified # of unique values
    #               thres: Ratio of unique pattern variants to total unique
    #                      series values
    #
    #     Description:  The purpose of this function is to identify repeated
    #     patterns that occur at the begining or end of every record.
    #
    #     Argument/Return:  The function requires a pandas series as an input,
    #     and returns the repeated patterns, as well as their relative location
    #     from the start/end of the string.
    #
    # =========================================================================

    #Set initial values
    chop_locs = []
    chop_loc = 0
    patterns = []

    #Check series type
    if s.dtype != 'object':
        return chop_loc, patterns

    #Find unique values and remove boolean
    unique = list(s[s.notnull()].unique())
    if True in unique:
        unique.remove(True)
    if False in unique:
        unique.remove(False)

    #Return null if series doesn't contain any unique, non-boolean values
    if len(unique) == 0:
        return chop_loc, patterns

    #Set maximum chop limit based on minimum string length in series
    len_min = len(min(unique, key=len))

    #Define list to iterate through
    iter_list = list(reversed(range(char_min, len_min)))

    #Iterate from start/end from char_min to len_min
    for i in iter_list:
        #Determine unique values for i chop length
        if search == 'start':
            n_unique = s[s.notnull()].str[:i].nunique()
        elif search == 'end':
            n_unique = s[s.notnull()].str[-i:].nunique()
        else:
            print('Error:  Enter Valid Search Direction')
            return chop_loc, patterns

        #Store value if n_unique qualifies for min/max limits
        if (n_unique >= nuq_min) & (n_unique <= nuq_max) & (n_unique/len(unique) <= thres):
            chop_locs.append(i)

    #Check if list is empty
    if len(chop_locs) > 0:

        #Determine max chop location that meets the requirements
        chop_loc = max(chop_locs)

        #
        if search == 'start':
            patterns = list(s[s.notnull()].str[:chop_loc].unique())
        elif search == 'end':
            patterns = list(s[s.notnull()].str[-chop_loc:].unique())
        else:
            print('Error:  Enter Valid Search Direction')

    return chop_loc, patterns


def chopsubstrings( pddf , exclude = None, inplace = False):

    # =========================================================================
    #     Function: chopsubstrings( pddf , exclude = None, inplace = False)
    #
    #     Description:  The purpose of this function is to identify and remove
    #     repeated patterns that occur at the begining or end of every record.
    #
    #     Argument/Return:  The function requires a pandas dataframe as an
    #     input,as well as an optional argument to exclude specific columns.
    #
    #     Details: If a repeated pattern is found, it will be reported in
    #     console and then removed from each record.
    # =========================================================================

    #Gather Columns
    df  = pddf.copy(deep = True)
    cols = list(df.select_dtypes('object').columns)

    #Remove excluded columns
    if exclude != None:
        for exclusion in exclude:
            cols.remove(exclusion)

    #Iterate through columns
    for col in cols:

        #Set Intial Values
        chop_start_text = ''
        chop_end_text = ''

        #Define Series
        s = df[col]

        #Find chop location and patterns from START
        chop_start_loc, patterns_start = chopseries(s,
                                                    search = 'start',
                                                    nuq_min = 1,
                                                    nuq_max = 1,
                                                    char_min = 1,
                                                    thres = 1
                                                    )

        #Define the start text that is being chopped
        if len(patterns_start) > 0:
            chop_start_text = patterns_start[0]

        #Find chop location and patterns from END
        chop_end_loc, patterns_end = chopseries(s,
                                                search = 'end',
                                                nuq_min = 1,
                                                nuq_max = 1,
                                                char_min = 1,
                                                thres = 1
                                                )

        #Define the text that is being chopped
        if len(patterns_end) > 0:
            chop_end_text = patterns_end[0]

        #Print result header
        if (len(chop_start_text) > 0) | (len(chop_end_text) > 0):
            print('\nModifying Column:  %s' % col)

        #Chop Start
        if len(chop_start_text) > 0:
            print('   Removing "%s" from start' % chop_start_text)
            if inplace:
                pddf[col] = pddf[col].str[chop_start_loc:]
            else:
                df[col] = df[col].str[chop_start_loc:]

        #Chop End
        if len(chop_end_text) > 0:
            print('   Removing "%s" from end' % chop_end_text)
            if inplace:
                pddf[col] = pddf[col].str[:-chop_end_loc]
            else:
                df[col] = df[col].str[:-chop_end_loc]

    if not inplace:
        return df

def splitsubstrings( pddf , exclude = None, nuq_max = 5, inplace = False):

    # =========================================================================
    #     Function: chopsubstrings( pddf , exclude = None, inplace = False)
    #
    #     Description:  The purpose of this function is to identify and remove
    #     repeated patterns that occur at the begining or end of every record.
    #
    #     Argument/Return:  The function requires a pandas dataframe as an
    #     input,as well as an optional argument to exclude specific columns.
    #
    #     Details: If a repeated pattern is found, it will be reported in
    #     console and then removed from each record.
    # =========================================================================

    #Import
    import numpy as np

    #Gather Columns
    df  = pddf.copy(deep = True)
    cols = list(df.select_dtypes('object').columns)

    #Remove excluded columns
    if exclude != None:
        for exclusion in exclude:
            cols.remove(exclusion)

    #Iterate through columns
    for col in cols:

        #Define Series
        s = df[col]

        #Find chop location and patterns
        for srch in ['start', 'end']:
            chop_loc, patterns = chopseries(s,
                                            search = srch,
                                            nuq_min = 2,
                                            nuq_max = nuq_max,
                                            char_min = 5,
                                            thres = 0.5
                                            )

            if chop_loc > 0:
                print('\nSplitting %s of column "%s", unique substrings:' % (srch, col))

                #Create reference column for matching
                if inplace:
                    pddf['ref'] = pddf[col]
                else:
                    df['ref'] = df[col]

                #Create new column for new categorical variable
                col_new = col + '_' + srch
                if inplace:
                    pddf[col_new] = np.nan
                else:
                    df[col_new] = np.nan

                #Iterate through sub-patterns
                for pat in patterns:
                    if srch == 'start':
                        s_sub = s[s.str[:chop_loc] == pat]
                    if srch == 'end':
                        s_sub = s[s.str[-chop_loc:] == pat]

                    #Find sub-chop location and patterns
                    chop_loc_sub, patterns_sub = chopseries(s_sub,
                                                            search = srch,
                                                            nuq_min = 1,
                                                            nuq_max = 1,
                                                            char_min = 5,
                                                            thres = 1
                                                            )

                    pat_sub = patterns_sub[0]
                    print('    "%s"' % pat_sub)

                    if srch == 'start':
                        #Strip from start
                        s_new = s.str[chop_loc_sub:]
                        if inplace:
                            pddf[col_new] = np.where(pddf['ref'].str[:chop_loc] == pat_sub, pat_sub, pddf[col_new])
                            pddf[col][pddf[col].str[:chop_loc] == pat] = s_new

                        else:
                            df[col_new] = np.where(df['ref'].str[:chop_loc] == pat_sub, pat_sub, df[col_new])
                            df[col][df[col].str[:chop_loc] == pat] = s_new

                    if srch == 'end':
                        #Strip from end
                        s_new = s.str[:-chop_loc_sub]
                        if inplace:
                            pddf[col_new] = np.where(pddf['ref'].str[-chop_loc_sub:] == pat_sub, pat_sub, pddf[col_new])
                            pddf[col][pddf[col].str[-chop_loc:] == pat] = s_new
                        else:
                            df[col_new] = np.where(df['ref'].str[-chop_loc_sub:] == pat_sub, pat_sub, df[col_new])
                            df[col][df[col].str[-chop_loc:] == pat] = s_new

    #Remove REF column
    if inplace:
        pddf.drop(columns = 'ref', inplace = True)
    else:
        df.drop(columns = 'ref', inplace = True)

    if not inplace:
        return df

    return

def dropdupcol( df ):

# =============================================================================
#     Function: dropdupcol( df )
#
#     Description:  The purpose of this function is to identify and remove
#     duplicate columns within a pandas dataframe.
#
#     Argument/Return:  The function requires a pandas dataframe as an input,
#     and returns a pandas dataframe with the duplicate columns removed.
#
#     Details: If a duplicate is found, the function will keep the first
#     instance and remove the second instance, based on the inital column
#     order.
# =============================================================================

    #Define list of columns
    cols = list(df.columns)
    cols_drop = []
    # Loop through pairs evaluate
    for col_1 in cols:
        for col_2 in cols:

            # Skip duplicate pairs (i.e. pair in lower triangular matrix)
            if cols.index(col_1) >= cols.index(col_2):
                continue

            # Skip if NA count doesn't match
            if df[col_1].isnull().sum() != df[col_2].isnull().sum():
                continue

            # Determine Index of NA Values
            index_na_1 = df[col_1].index[df[col_1].isnull()]
            index_na_2 = df[col_2].index[df[col_2].isnull()]
            test_na = list(~(index_na_1 == index_na_2))
            test_vals = list(~(df[col_1][df[col_1].notna()] == df[col_2][df[col_2].notna()]))

            # Flag if columns have identical values
            if (sum(test_na) + sum(test_vals)) == 0:
                #Print and store result
                print('Duplicate Columns: %s, %s' % (col_1, col_2))
                cols_drop.append(col_2)

    #Remove Duplicates from Drop List
    cols_drop = list(set(cols_drop))

    #Print dropped columns and drop from dataframe
    print('\nDropping Columns:  ')
    for col in cols_drop:
        print('    %s' % col)
        df.drop(columns = col, inplace=True)

    return

def estlatlong( df , est_by,  inplace=False):

    #Fill in using average Trailhead location (if available)
    df_temp = df.groupby(by=est_by, as_index=False).agg({'Lat':np.mean,'Long':np.mean}, axis=1)
    df_temp.rename(columns={'Lat': 'Lat_est', 'Long': 'Long_est'}, inplace=True)

    #Track initial null values
    null_cnt_0 = df.Lat.isnull().sum()

    df = df.merge(df_temp, on=est_by)
    df['Coord_Type'] = np.where(df.Lat.isnull(), 'Est - ' + est_by, 'Actual')
    df.Lat = np.where(df.Lat.isnull(), df.Lat_est, df.Lat)
    df.Long = np.where(df.Long.isnull(), df.Long_est, df.Long)

    #Track final null values
    null_cnt_1 = df.Lat.isnull().sum()

    #Drop temporary merged columns
    df.drop(['Lat_est', 'Long_est'], axis=1, inplace=True)

    #Print results
    print('Null values reduced from %d to %d' % (null_cnt_0, null_cnt_1))

    return df


























