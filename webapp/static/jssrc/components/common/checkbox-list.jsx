const React = require("react");
const ReactDOM = require("react-dom");

const CheckboxList = React.createClass({
    render(){
        var self = this;
        var items = this.props.data.map(function(data){
            return (
                <li key={"cb"+data.key} className="border-bottom border-silver">
                    <label htmlFor={data.key} className="block p1 hover-darken">
                        <input type="checkbox" defaultChecked={data.default} ref={data.key} name={data.key} id={data.key} className="field" onChange={self.handleChange}/>
                        <span className="ml1">{data.label}</span>
                    </label>
                </li>
            )
        });
        return (
            <ul className="list-reset">
                {items}
            </ul>
        );
    },
    getValues(){
        var values = {}
        for(var i=0; i<this.props.data.length; i++){
            var d = this.props.data[i];
            values[d.key] = ReactDOM.findDOMNode(this.refs[d.key]).checked;
        }
        return values;
    }
});

module.exports = CheckboxList;;
