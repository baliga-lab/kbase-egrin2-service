#BEGIN_HEADER
import tempfile
import os
import json

import shock
import awe
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
        result = shock_client.upload_file(tmpfile.name)
        os.unlink(tmpfile.name)
        builder = awe.WorkflowDocumentBuilder('pipeline', 'name', 'default', 'ubuntu', 'kbase')
        command = Command("cat", "@infile > /home/ubuntu/AWE_fromshock.txt")
        task = Task(command, 1)
        task.add_shock_input('infile', self.config['shock_service_url', tmpfile.name])
        builder.add_task(task)

        awe_tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        awe_tmp.write(json.dumps(builder.doc))
        awe_tmp.close()
        awe_client = awe.AWEClient(self.config['awe_service_url'], ctx['token'])
        awe_client.submit_job(awe_tmp.name)
        os.unlink(awe_tmp.name)
        print "RESULT OF SHOCK: ", result

        jobid = "12345"
        #END run_ensemble

        # At some point might do deeper type checking...
        if not isinstance(jobid, basestring):
            raise ValueError('Method run_ensemble return value ' +
                             'jobid is not type basestring as required.')
        # return the results
        return [jobid]
