#BEGIN_HEADER
import tempfile
import os
import json
import shock
import awe
import egrin2
import traceback

import biokbase.workspace.client as wsc

# Define the executables as constants so we can replace them with mock programs
# for testing
CM2_RUNNER = 'mock_cm2_runner.py'
CM2AWE = 'mock_cm2awe.py'
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
        print "workspace service at: %s" % self.config['ws_service_url']
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

        ws_service = wsc.Workspace(self.config['ws_service_url'], token=ctx['token'])
        try:
            print "trying to create workspace '%s'..." % params['target_ws']
            ws_service.create_workspace({'workspace': params['target_ws']})
            print "workspace created."
        except:
            print "workspace exists or unknown error"
        egrin2.store_ratios(ws_service, params['target_ws'], params['ratios'])

        ratios_file_id = shock.upload_data(params['ratios'],
                                           self.config['shock_service_url'],
                                           ctx['token'])
        has_blocks = False
        if "block_defs" in params:
            blocks = params["block_defs"]["blocks"]
            inclusion_blocks = params["block_defs"]["inclusion_blocks"]
            exclusion_blocks = params["block_defs"]["exclusion_blocks"]

            blocks_file_id = shock.upload_data(blocks,
                                               self.config['shock_service_url'],
                                               ctx['token'])
            inclusion_file_id = shock.upload_data(inclusion_blocks,
                                                  self.config['shock_service_url'],
                                                  ctx['token'])
            exclusion_file_id = shock.upload_data(exclusion_blocks,
                                                  self.config['shock_service_url'],
                                                  ctx['token'])
            has_blocks = True

        print "building workflow document"
        builder = awe.WorkflowDocumentBuilder('pipeline', 'name', project='default',
                                              user='nwportal', clientgroups='kbase')
        awe_tmp = None
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
            if has_blocks:
                task.add_shock_input('block_file', self.config['shock_service_url'], node=blocks_file_id)
                task.add_shock_input('inclusion_file', self.config['shock_service_url'], node=inclusion_file_id)
                task.add_shock_input('exclusion_file', self.config['shock_service_url'], node=exclusion_file_id)

            task.add_shock_output('splitter_out', self.config['shock_service_url'], filename='splitter_out')
            builder.add_task(task)

            # Step 2: cmonkey2 runner
            #run_nums = range(1, num_runs + 1)
            run_nums = [1, 2]
            dbfiles = ["cmonkey_run-%03d.db" % i for i in [1, 2]]

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

            # Step 3a: The assemble step
            task_id = run_nums[-1] + 1  # we pick the next available id
            assembler_task_id = task_id
            arg_string = '--organism %s --targetdir /tmp --dbengine sqlite --targetdb result_db --ratios @ratios_file' % (params["organism"])
            input_files = ['@' + dbfile for dbfile in dbfiles]
            arg_string = arg_string + ' ' + ' '.join(input_files)
            assemble_command = awe.Command('assembler.py', arg_string,
                                           environ={"private": {"KB_AUTH_TOKEN": ctx['token']},
                                                    "public": {"SHOCK_URL": self.config['shock_service_url'],
                                                                "LOG_DIRECTORY": self.config['awe_client_logdir'],
                                                                "WS_URL": self.config['ws_service_url'],
                                                                "TARGET_WS": params['target_ws']}})
            task = awe.Task(assemble_command, str(assembler_task_id), depends_on=map(str, run_nums))
            task.add_shock_input('ratios_file', self.config['shock_service_url'], node=ratios_file_id)
            for run_num, dbfile in zip(run_nums, dbfiles):
                task.add_shock_input(dbfile, self.config['shock_service_url'], origin=str(run_num))
            task.add_shock_output("result_db", self.config['shock_service_url'], filename="result_db")
            builder.add_task(task)

            # Submit
            print builder.doc

            awe_tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
            awe_tmp.write(json.dumps(builder.doc))
        except:
            traceback.print_exc()
        finally:
            if awe_tmp is not None:
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
