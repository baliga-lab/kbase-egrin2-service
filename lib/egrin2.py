def store_ratios(ws_service, target_ws, ratios):
    expmat = [row.split('\t') for row in ratios.split('\n')]
    col_names = expmat[0]
    row_names = [row[0] for row in expmat]
    values = [map(float, row[1:]) for row in expmat]
    data = {'row_names': row_names, 'col_names': col_names,
            'values': values}
    try:
        res = ws_service.save_object({'type': 'egrin2isb.SimpleGeneExpressionMatrix-0.1',
                                      'data': data,
                                      'workspace': target_ws})
        print "gene expression stored to target workspace"
        print res
    except Exception, e:
        print e
