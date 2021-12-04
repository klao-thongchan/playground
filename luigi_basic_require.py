import luigi
 
class BasicTask(luigi.Task):

  def requires(self): 
    [FileExistsTask(self.input_filepath)]