/* These are the type definitions for the persistent data types
of the EGRIN2 service */
module egrin2isb {
    typedef structure {
        list<string> row_names;
        list<string> col_names;
        list<list<float>> values;
    } SimpleGeneExpressionMatrix;

    typedef structure {
        string seq_name;
        boolean reverse;
        int start;
        float pvalue;
    } MotifSite;

    typedef structure {
        float a;
        float c;
        float g;
        float t;
    } PSSMRow;

    typedef structure {
        string seqtype;
        int motif_num;
        float evalue;
        list<MotifSite> sites;
        list<PSSMRow> pssm_rows;
    } Motif;

    typedef structure {
        float residual;
        int num;
        list<string> row_names;
        list<string> col_names;
        list<Motif> motifs;
    } Bicluster;

    typedef structure {
        string name;
        float pvalue;
    } CoremColumn;

    typedef structure {
        string row1;
        string row2;
    } CoremEdge;

    typedef structure {
        int num;
        float density;
        float weighted_density;
        list<string> rows;
        list<CoremColumn> columns;
        list<CoremEdge> edges;
    } Corem;

    typedef structure {
        string date_added;
        string start_time;
        string finish_time;
        int num_iterations;
        string organism;
        string species;
        list<string> row_names;
        list<string> column_names;
        list<Bicluster> clusters;
    } EnsembleRun;

    typedef structure {
        list<string> run_ids;
        string expression_id;
        list<string> corem_ids;
    };
};
