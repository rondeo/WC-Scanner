let websocket;
let instance = null;

export default class websocketUtil {

    constructor(props){
        this.remote_server_address = "ws://192.168.99.103:6789";
        this.props = props;
        this.connectionStatue();
    }

    connectionStatue() {
        let that = this;
        websocket = new WebSocket(this.remote_server_address);

        websocket.onmessage = function(event) {
            let data = JSON.parse(event.data);
            switch (data.type) {
                case 'projects_data':
                    that._stateListProject(data.data);
                    break;
                default:
                    console.error(
                        "unsupported event", data);
            }
        };

        websocket.onopen = () => {
            that._stateConnectionTrue();
        };

        websocket.onclose = () => {
            that._stateConnectionFalse();
        };

    }

    turn_bed_CCW_trigger(angle) {
        websocket.send(JSON.stringify({
            action: "turn_bed_CCW",
            plateau_degree: angle
        }))
    }

    turn_bed_CW_trigger(angle) {
        websocket.send(JSON.stringify({
            action: "turn_bed_CW",
            plateau_degree: angle
        }))
    }

    create_project(project) {
        websocket.send(JSON.stringify({
            action: "create_project",
            project_name: project.project_name,
            description: project.project_description,
            pict_per_rotation: project.project_ppr,
            pict_res: project.project_picture_resolution,
        }))
    }

    request_remove_project(project_name){
        websocket.send(JSON.stringify(
            {action: "request_remove_project", project_name: project_name}
        ))
    }

    start_loop_capture(project_name){
        websocket.send(JSON.stringify({
            action: "loop_capture",
            project_name: project_name
        }))
    }

    //REDUX
    _stateConnectionFalse() {
        let action = { type: "STATE_CHANGE", value: false };
        this.props.dispatch(action)
    }

    _stateConnectionTrue() {
        let action = { type: "STATE_CHANGE", value: true };
        this.props.dispatch(action)
    }

    _stateListProject(data){
        let action = { type: "STATE_RELOAD_LISTPROJECT", value: data};
        this.props.dispatch(action);
    }

}