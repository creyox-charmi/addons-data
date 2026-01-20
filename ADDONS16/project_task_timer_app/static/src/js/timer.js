/** @odoo-module **/

import { registry } from "@web/core/registry";
const { Component, useState, onWillUpdateProps, onWillStart, onWillDestroy } = owl;
var time = require('web.time');
var rpc = require('web.rpc');
console.log("loaddddddddddddddddddddddddddddd")

export class PTTimer extends Component {
	setup() {
		let self = this;
		let data = this.props.record.data;
		this.state = useState({duration: 0});
		onWillStart(() => self._runTimer());
		onWillDestroy(() => clearTimeout(this.timer));
		this._startTimeCounter();
		console.log("setup-===================",this)
		onWillUpdateProps((nextProps) => {
			console.log(self,"nextProps-===================",nextProps)
			self._startTimeCounter();
			// location.reload();
		});
	}

	_startTimeCounter() {
		var self = this;
		console.log("_startTimeCounter-=-------------",this);
		clearTimeout(this.timer);
        if (this.props.record.data.is_user_working) {
            this.timer = setTimeout(function () {
                self.state.duration += 1000;
                self._startTimeCounter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
	}

	get checkRunning(){
		let running = false;
		if(this.props.record.data.is_started){
			running = true;
		}
		return running;
	}

	
	async _runTimer() {
		var self = this;
		console.log("_runTimer==============",self)
		var def = await rpc.query({
			model: 'project.calculate.duration',
			method: 'search_read',
			domain: [
				['production_id', '=', self.props.record.resId],
			],
		}).then(function (result) {
			// if (self.props.readonly === true) {
				console.log("result====================",result)
				var currentDate = new Date();
				_.each(result, function (data) {
					let dd = data.date_end ?
						self._getDateDifference(data.date_start, data.date_end) :
						self._getDateDifference(time.auto_str_to_date(data.date_start), currentDate);
					console.log(dd,"dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data)
					self.state.duration += dd;
				});
			// }
		});
	}

	_getDateDifference(dateStart, dateEnd) {
		return moment(dateEnd).diff(moment(dateStart));
	}

	get durationFormatted() {
		
		let value = this.state.duration;
		// console.log(this,"durationFormatted====================",value)
		if (value === false) {
			return "";
		}
		const isNegative = value < 0;
		if (isNegative) {
			value = Math.abs(value);
		}
		return moment.utc(value).format("HH:mm:ss")
	}
}

PTTimer.supportedTypes = ["float"];
PTTimer.template = "project_task_timer_app.PTTimer";
registry.category("fields").add("task_time_counter", PTTimer);