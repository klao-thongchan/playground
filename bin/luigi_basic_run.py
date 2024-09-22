class LoadTask(luigi.Task):

file_path = luigi.Parameter()
    def run(self):
        cnx = mysql.connector.connect(user='joe', database='test')
        stmt = "insert into basic_date(col1,col2,col3)  select distinct col1, col2, col3 from table1" 
        curs=cnx.cursor()
        curs.execute(stmt)
        curs.commit()
        curs.close()
        with self.output().open('w') as out_file:
            print >> out_file, strDate1, strDate2
    def output(self):
            return luigi.file.LocalTarget(path='/tmp/123')