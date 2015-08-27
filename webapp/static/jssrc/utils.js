var utils = {
    encodeQueryString(obj) {
        var pairs = [];
        for(var key in obj){
            if(obj.hasOwnProperty(key) && obj[key] !== void(0)) {
                pairs.push(key + "=" + encodeURIComponent(obj[key]));
            }
        }
        return "?" + pairs.join("&");
    },
    unique(a){
        return a.filter(function(item, pos, self) {
            return self.indexOf(item) == pos;
        })
    },
    naturalSort(strings, key){
        var sorted = strings.sort((a, b) => {
            if(key){
                a = key(a);
                b = key(b);
            }
            a = a.trim().toLowerCase();
            b = b.trim().toLowerCase();

            if(a.startsWith("the ")){
                a = a.slice(4).trim();
            }
            if(b.startsWith("the ")){
                b = b.slice(4).trim();
            }
            console.log("comparing "+a+" and "+b);
            if(a < b){
                return -1
            } else if(b < a){
                return 1
            }else{
                return 0
            }
        });
        console.log("sorted:");
        console.log(sorted);
        return sorted;
    }
};

module.exports = utils;
