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
        tmpfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        tmpfile.write(params['ratios'])
        tmpfile.close()
        print "the TMPFILE IS: ", tmpfile.name

        shock_client = shock.ShockClient(self.config['shock_service_url'], ctx['token'])
        try:
          print "uploading input file ..."
          shock_result = shock_client.upload_file(tmpfile.name)
          print shock_result
          file_id = shock_result['data']['id']
        except:
          print "error uploading file"
          traceback.print_exc()
          os.unlink(tmpfile.name)

        print "building workflow document"
        builder = awe.WorkflowDocumentBuilder('pipeline', 'name', project='default',
                                              user='nwportal', clientgroups='kbase')
        try:
          #command = awe.Command("cat", "@infile > /home/ubuntu/AWE_fromshock.txt")
          command = awe.Command("cp", "@infile /tmp/mytestfile")
          task = awe.Task(command, "0")
          task.add_shock_input('infile', self.config['shock_service_url'], file_id)
          builder.add_task(task)
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
