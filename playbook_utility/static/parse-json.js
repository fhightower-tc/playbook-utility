function parseJson() {
    // get the response data
    var rawData = $('#responseContent').val().replace(/'/g, '"');
    var jsonData = JSON.parse(rawData);
    // parse and output the content
    $('#json-renderer').jsonPathPicker(jsonData, '#path', {
        pathQuotesType: 'double'
    });
}

var jsonPathVue = new Vue({
    el: "#content",
    data: {
        jsonPaths: [],
        path: "",
        name: "",
    },
    methods: {
        addPath: function() {
            /* Add a json path and name to the list of paths. */
            if (this.path === '') {
                $.jGrowl('Please select a json path by clicking on one of the clipboards beside the value you would like to select.');
                return;
            }

            if (this.name === '') {
                $.jGrowl('Please enter a name for the json path as you would like to appear in the output variable of the "Json Path" app.');
                return;
            }

            this.jsonPaths.push({
                path: this.path,
                name: this.name
            });
            $.jGrowl('Path added!');
            this.path = "";
            this.name = "";
        },
        nameFocus: function() {
            /* Focus on the 'name' field. */
            // the timeout below is required so the value of the name field is filled in first and is then selected
            window.setTimeout(function() {
                $('#name').select();
            }, 100)
        }
    }
});
