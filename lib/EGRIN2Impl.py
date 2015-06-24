#BEGIN_HEADER
import tempfile
import os
import json
import shock
import awe
import traceback

# Define the executables as constants so we can replace them with mock programs
# for testing
CM2_RUNNER = 'cm2_runner.py'
CM2AWE = 'cm2awe.py'
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
        num_runs = params['num_runs']

        print "# RUNS: %d" % num_runs
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
            # Step 1: Splitter
            command = awe.Command(CM2AWE,
                                  "--organism %s --nruns %d --ratios  @ratios_file --outfile splitter_out --blocks @block_file --inclusion @inclusion_file --exclusion @exclusion_file" % (params["organism"],
                                                                                                                                                                                           num_runs),
                                  environ={"private": {"KB_AUTH_TOKEN": ctx['token']},
                                           "public": {"SHOCK_URL": self.config['shock_service_url'],
                                                      "LOG_DIRECTORY": self.config['awe_client_logdir']}})

            task = awe.Task(command, "0")
            task.add_shock_input('ratios_file', self.config['shock_service_url'], node=ratios_file_id)
            task.add_shock_input('block_file', self.config['shock_service_url'], node=blocks_file_id)
            task.add_shock_input('inclusion_file', self.config['shock_service_url'], node=inclusion_file_id)
            task.add_shock_input('exclusion_file', self.config['shock_service_url'], node=exclusion_file_id)

            task.add_shock_output('splitter_out', self.config['shock_service_url'], filename='splitter_out')
            builder.add_task(task)

            # Step 2: cmonkey2 runner
            #run_nums = range(1, num_runs + 1)
            run_nums = [1, 2]
            dbfiles = ["cmonkey_db_%03d" % i for i in [1, 2]]

            for run_num, dbfile in zip(run_nums, dbfiles):
                cm_command = awe.Command(CM2_RUNNER,
                                         "--organism %s --inputfile @splitter_out --run_num %d --outdb %s" % (params['organism'], run_num, dbfile),
                                         environ={"private": {"KB_AUTH_TOKEN": ctx['token']},
                                                  "public": {"SHOCK_URL": self.config['shock_service_url'],
                                                             "LOG_DIRECTORY": self.config['awe_client_logdir']}})
                task = awe.Task(cm_command, "%d" % run_num, depends_on=["0"])
                task.add_shock_input('splitter_out', self.config['shock_service_url'], origin="0")
                task.add_shock_output(dbfile, self.config['shock_service_url'], filename=dbfile)
                builder.add_task(task)

            # Step 3: The assemble steps
            task_id = run_nums[-1] + 1  # we pick the next available id

            # 3a. Merge runs into a large database
            # 3b. Make corems
            # 3c. Run resampling
            # 3d. Finish assembling

            # Step 4: Postprocessing steps

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
