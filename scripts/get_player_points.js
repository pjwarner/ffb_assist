function get_stats(POS, OPP){
    var a = db.players.group({
        cond:{"POS":POS, "STATS.OPP":OPP}
        , key: {}
        , initial: {count:0, points:0}
        , reduce: function(doc, out){
            out.count++; out.points+=doc.STATS.FAN_POINTS}
        , finalize: function(out){
            out.avg_points = out.points / out.count}
    });
    return a
}