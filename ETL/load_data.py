def unzip_files():

    # function unzips all zipfiles in sourcepath folder, extracts the file with the given suffix,
    # and names the extracted file after the zipfile (since the csv file names within don't describe
    # contents)

    import zipfile
    import os
    import pandas as pd
    import re

    # create variables to hold directory to pull .zip files from, directory to deposit extracted .csvs into,
    # and csv name ending to extract
    sourcepath = "../data/"
    targetpath = "../data/extracted/"
    suffix = "_Data.csv"

    # create a directory to deposit extracted .csvs into
    if os.path.isdir(targetpath) == False:
        os.mkdir(targetpath)

    # extract .csv ending in _Data.csv from each .zip file, name .csv file after .zip file,
    # and deposit into the targetpath
    for file in os.listdir(sourcepath):  # loop through items in dir
        if file.endswith(".zip"):
            totalfilepath = os.path.join(sourcepath, file)  # get zip file path
            with zipfile.ZipFile(totalfilepath) as zf:  # open the zip file
                for item in zf.namelist():  # loop through the list of files to extract
                    if re.search(rf'{suffix}\Z', str(item)):
                        filename = file.replace(".zip","") + ".csv" # replace .zip with .csv
                        filepath = os.path.join(targetpath, filename)  # output path
                        with open(filepath, "wb") as f:  # open the output path for writing
                            f.write(zf.read(item))  # save the contents of the file in it


def returncaps(string):
    # helper function creates acronym from the uppercase initials in filename
    acronym = []
    for char in string:
        if char.isupper():
            acronym.append(char)
    return ''.join(acronym)


def getlower(string):
    # helper function gets the indices of the lowercase letters in a string
    # used below in case of files with same acronym, adds a lower case
    # letter to distinguish the two
    lowerlist = []
    while len(lowerlist) == 0:
        for index, char in enumerate(string):
            if char.islower():
                lowerlist.append(index)
    return lowerlist[0]  

def separate_csv():
    # function separates csv files created by unzip_files() function into constituent dfs,
    # each containing data for specific database table, adds country income info,
    # and exports to csv

    import os
    import pandas as pd
    import re

    # create directory to deposit separated dfs
    csv_path = "../data/extracted/separated/"
    target_path = "../data/extracted/"
    source_path = "../data/"
    if os.path.isdir(csv_path) == False:
        os.mkdir(csv_path)

    # create list to store file name acronyms
    file_acros = []

    # iterate through csv files extracted from zips
    for file in os.listdir(target_path):
        # drop the csv suffix from file
        file_name = file.replace('.csv','')
        # create acronym of file_name to use for writing final .csv files
        file_name_acro = returncaps(file_name) # create filename acronym
        # if file name acronym already exists, create new one with first lower case
        # letter inserted, else just use file name acronym (keep record of acronyms in
        # file_acros list)
        if file_name_acro in file_acros:
            lower_letter = getlower(file_name)
            file_name_acro = file_name_acro[:lower_letter] + \
                file_name[lower_letter] + file_name_acro[lower_letter:]
            file_acros.append(file_name_acro)
        else:
            file_acros.append(file_name_acro)
        # for csv files in targetpath folder, read into df, drop metadata (bottom 5 rows),
        # delete year from year column heading which leaves 'yr____', create list of unique rows from column 2
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(target_path + file))
            df = df[:-5]
            df.drop(labels='Series Code', axis = 1, inplace = True)
            col_move1 = df.pop("Country Name")
            df.insert(0, "Country Name", col_move1)
            col_move2 = df.pop("Country Code")
            df.insert(0, "Country Code", col_move2)
            for column in df.columns:
                if column[0].isnumeric():
                    df.rename({column:column[6:12]}, axis='columns', inplace=True)
            df_rows = df.iloc[:,2].unique()

            # load income groups csv into df
            income_groups = pd.read_csv(os.path.join(source_path + "income_groups.csv"))

            # create a separate df consisting of all rows that share a common unique column 2 value, clean column 2
            # value entries, write each separate df to the csv_path directory
            for item in df_rows:
                grouped_df = df.groupby(df.iloc[:,2])
                df_new = grouped_df.get_group(item)
                csv_name = df_new.iloc[0,2]
                csv_name = re.sub(r'(?<=.) \(.+\)','', csv_name)
                csv_name = csv_name.replace(',', '')
                csv_name = csv_name.replace(' ', '_')
                csv_name = csv_name.replace(',', '')
                # df_new.iloc[:,2].replace(r'(?<=.) \(.+\)','', regex=True, inplace=True)
                df_new.iloc[:,2].replace(', ', ' ', regex=True, inplace=True)
                # df_new.iloc[:,2].replace(' ', '_', regex=True, inplace=True)
                df_new.iloc[:,1].replace(',', '', regex=True, inplace=True)
                
                # Write as optional function call
                # Transpose the dataframe with the years in the rows and the countries in the columns
                # df_T = df_new.T
                # df_T.columns = df_T.iloc[0]
                # df_T.drop(["Country Name","Series Name", "Country Code"], axis = 0, inplace=True)
                # df_T.columns.name = None
                # df_T.reset_index(inplace=True)
                # df_T.rename(columns= {"index":"Year"}, inplace=True)

                # join df with income_groups.csv df (and drop redundant columns) to link income group to country
                merged_df = df_new.merge(income_groups, 'inner', left_on = 'Country Code', right_on = 'Code')
                first_col = merged_df.pop('Income Group')
                merged_df.insert(1, 'Income Group', first_col)
                merged_df.drop(['Code', 'Table Name'], axis = 1, inplace = True)    

                # Because upper case in SQL table names is illegal, lowering case of file names
                # here so that table names can be named after them later
                # lowerfilename = (os.path.join((file_name_acro + '_' + csv_name + '.csv').lower()))
                lowerfilename = (os.path.join((csv_name + '.csv').lower()))
                merged_df.to_csv(os.path.join(csv_path + lowerfilename), index=False)


def convertdtypes(list):
    # help function creates a list of sql data types from python counterparts
    sql_types = []
    for item in list:
        if item == 'float64':
            sql_types.append('numeric')
        elif item == 'object':
            sql_types.append('text')
    return sql_types


def create_tables():
# function programmatically creates db relation and loads data from csv file into
# corresponding relation using psycopg2 library

    import os
    import psycopg2
    from psycopg2 import sql
    import pandas as pd

    csv_path = "../data/extracted/separated/"

    # Define database connection variables using environmental variables
    DB_NAME = os.environ['DBNM']
    DB_USER = os.environ['DBUS']
    DB_PASS = os.environ['DBPS']
    DB_HOST = os.environ['DBHS']
    DB_PORT = os.environ['DBPT']

    # connect to database
    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
    except:
        print("Database not connected successfully")
    cur = conn.cursor() # create a cursor

    prec = 2 # define precision of postgres numerical type 

    # iterate through each file in path of separated csv files
    for file in os.listdir(csv_path):
        # clean the filenames so they can be used as sql table names
        file_name = file.replace('.csv','')
        file_name = file_name.replace('.','')
        file_name = file_name.replace('$','')
        file_name = file_name.replace('%','')

        # read file as df, read and clean column names and data types (translated into sql data types)
        df = pd.read_csv(os.path.join(csv_path, file))
        col_list = df.columns
        col_list = [item.replace(' ', '_') for item in col_list]
        col_list = [item.lower() for item in col_list]
        dtypes_list = df.dtypes
        sql_types = convertdtypes(dtypes_list)

        # create list containing cleaned file name, column names, and sql data types
        sql_col_list = []
        for index, column in enumerate(col_list):
            sql_col_list.append([file_name, col_list[index], sql_types[index]])

        # create a sql table named after csv file, with first df column as primary key
        # query_create = sql.SQL("CREATE TABLE {table} ({field} {type} PRIMARY KEY)") # create column with df column name and data type
        # cur.execute(query_create.format(table = sql.Identifier(sql_col_list[0][0]), field = sql.Identifier(sql_col_list[0][1]), type = sql.Identifier(sql_col_list[0][2])))
        # conn.commit()
        query_create = sql.SQL("CREATE TABLE {table} ({field} {type} PRIMARY KEY)")
        cur.execute(query_create.format(table = sql.Identifier(sql_col_list[0][0]), field = sql.Identifier(sql_col_list[0][1]), type = sql.Identifier(sql_col_list[0][2])))
        conn.commit()    

        # add every other column in df
        for index in range(len(col_list) - 1): # for every other column except for first
            query_add = sql.SQL("alter table {table} add {field} {type}") # create column with df column name and data type
            cur.execute(query_add.format(table = sql.Identifier(sql_col_list[index+1][0]), field = sql.Identifier(sql_col_list[index+1][1]), type = sql.Identifier(sql_col_list[index+1][2])))
            conn.commit()       

        # load in data from corresponding csv
        with open(os.path.join(csv_path, file), 'r') as f:
            next(f)
            cur.copy_from(f, file_name, sep=',', null='')
            conn.commit()

    # close cursor and connection
    cur.close()
    conn.close()