#BEGIN_HEADER
import tempfile
import os
import json
import shock
import awe
import traceback
#END_HEADER


class EGRIN2:
    '''
    Module Name:
    EGRIN2

    Module Description:
    
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        print "AWE service at: %s" % self.config['awe_service_url']
        print "Shock service at: %s" % self.config['shock_service_url']
        print "UJS service at: %s" % self.config['shock_service_url']
	print config
        #END_CONSTRUCTOR
        pass

    def run_ensemble(self, ctx, params):
        # ctx is the context object
        # return variables are: jobid
        #BEGIN run_ensemble
        print "RUNNING ENSEMBLE"
        print "auth token: ", ctx['token']

        print "# RUNS: %d" % params['num_runs']
        print "organism: %s" % params['organism']
        blocks = params["block_defs"]["blocks"]
        inclusion_blocks = params["block_defs"]["inclusion_blocks"]
        exclusion_blocks = params["block_defs"]["exclusion_blocks"]

        ratios_file_id = shock.upload_data(params['ratios'],
                                           self.config['shock_service_url'],
                                           ctx['token'])
        blocks_file_id = shock.upload_data(blocks,
                                           self.config['shock_service_url'],
                                           ctx['token'])
        inclusion_file_id = shock.upload_data(inclusion_blocks,
                                           self.config['shock_service_url'],
                                           ctx['token'])
        exclusion_file_id = shock.upload_data(exclusion_blocks,
                                           self.config['shock_service_url'],
                                           ctx['token'])

        print "building workflow document"
        builder = awe.WorkflowDocumentBuilder('pipeline', 'name', project='default',
                                              user='nwportal', clientgroups='kbase')
        try:

          command = awe.Command("cm2awe.py", "--organism %s --ratios  @ratios_file --targetdir /home/ubuntu/splitting_awe --blocks @block_file --inclusion @inclusion_file --exclusion @exclusion_file" % params["organism"])
          task = awe.Task(command, "0")
          """
          --organism mtb --ratios mtb_files/20141130.MTB.all.ratios.csv --targetdir splitting_awe --blocks mtb_files/20141202.MTB.EGRIN2.blocks.csv --inclusion mtb_files/20141202.MTB.EGRIN2.inclusion.blocks.csv --exclusion mtb_files/20141202.MTB.EGRIN2.exclusion.blocks.csv --nruns 100"""


          task.add_shock_input('ratios_file', self.config['shock_service_url'], node=ratios_file_id)
          task.add_shock_input('block_file', self.config['shock_service_url'], node=blocks_file_id)
          task.add_shock_input('inclusion_file', self.config['shock_service_url'], node=inclusion_file_id)
          task.add_shock_input('exclusion_file', self.config['shock_service_url'], node=exclusion_file_id)

          builder.add_task(task)

          """
          command = awe.Command("mycommand", "@block_file stage0_out")
          task = awe.Task(command, "0")

          task.add_shock_input('ratios_file', self.config['shock_service_url'], node=ratios_file_id)
          task.add_shock_input('block_file', self.config['shock_service_url'], node=blocks_file_id)
          task.add_shock_input('inclusion_file', self.config['shock_service_url'], node=inclusion_file_id)
          task.add_shock_input('exclusion_file', self.config['shock_service_url'], node=exclusion_file_id)

          task.add_shock_output('stage0_out', self.config['shock_service_url'], filename='stage0_out')
          builder.add_task(task)

          command2 = awe.Command("cp", "@stage0_out /home/ubuntu/final_file.txt")
          task2 = awe.Task(command2, "1", depends_on=["0"])
          task2.add_shock_input('stage0_out', self.config['shock_service_url'], origin="0")
          builder.add_task(task2)"""

          print builder.doc

          awe_tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
          awe_tmp.write(json.dumps(builder.doc))
        except:
          traceback.print_exc()
        finally:
          awe_tmp.close()

        try:
          print "submitting AWE job"
          awe_client = awe.AWEClient(self.config['awe_service_url'], ctx['token'])
          awe_result = awe_client.submit_job(awe_tmp.name)
          print awe_result
          jobid = awe_result['data']['id']
          print "job id: ", jobid
        except:
          print "ERRROR !!!!"
          traceback.print_exc()
        finally:
          os.unlink(awe_tmp.name)

        #END run_ensemble

        # At some point might do deeper type checking...
        if not isinstance(jobid, basestring):
            raise ValueError('Method run_ensemble return value ' +
                             'jobid is not type basestring as required.')
        # return the results
        return [jobid]
