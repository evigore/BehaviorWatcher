class Watcher {
	constructor(host, metric) {
		this.host = host;
		this.timer = undefined;
		this.totalTime = 0;
		this.idleTimeoutMs = 2 * 60 * 1000; // 2min
		this.delayBeforeSendMs = 5 * 1000;
		this.currentIdleTimeMs = 0;
		this.checkIdleStateRateMs = 250;
		this.isUserCurrentlyOnPage = true;
		this.isUserCurrentlyIdle = false;

		this.trackWhenUserLeavesPage = true;
		this.trackWhenUserGoesIdle = true;

		this.user = {
			user_id: metric.user_id,
			task_id: metric.task_id,
			reading_time: 0,
			task_copied: false,
			task_viewed: false
		};

		this.sendAllSavedData();
		this.listenEvents(metric.trackIdWhenCopies, metric.trackIdWhenViews);
		this.startTimer();
	}

	sendAllSavedData() {
		let keys = Object.keys(localStorage);
		for (let i = 0; i < keys.length; i++) {
			let data = JSON.parse(localStorage.getItem(keys[i]));
			this.removeFromStorage(keys[i]);

			this.sendSafe(data, (key, json) => {
				if (json === undefined)
					return;

				this.saveToStorage(json, key);
			});

		}
	}

	saveToStorage(value, key) {
		if (key === undefined)
			localStorage.setItem(this.user.task_id.toString(), value);
		else
			localStorage.setItem(key, value);
	}

	getFromStorage() {
		return localStorage.getItem(this.user.task_id.toString())
	}

	removeFromStorage(key) {
		if (key === undefined)
			localStorage.removeItem(this.user.task_id.toString());
		else
			localStorage.removeItem(key);
	}

	startTimer() {
		if (this.timer !== undefined && this.timer.stopTime === undefined)
			return;

		this.timer = {
			'startTime': new Date(),
			'stopTime': undefined
		};
	}

	stopTimer() {
		if (this.timer === undefined)
			return;

		this.timer.stopTime = new Date();
		this.totalTime += Number(this.timer.stopTime - this.timer.startTime);
		this.timer = undefined;
	}

	getTimeOnPageInMilliseconds() {
		let diff = 0;

		if (this.timer !== undefined) {
			let startTime = this.timer.startTime;
			let stopTime = this.timer.stopTime || new Date();
			diff = Number(stopTime - startTime);
		}

		return this.totalTime + diff;
	}

	userActivityDetected() {
		if (this.isUserCurrentlyIdle)
			this.triggerUserHasReturned();

		this.resetIdleCountdown();
	}

	resetIdleCountdown() {
		this.isUserCurrentlyIdle = false;
		this.currentIdleTimeMs = 0;
	}

	triggerUserHasReturned() {
		if (!this.isUserCurrentlyOnPage) {
			this.isUserCurrentlyOnPage = true;
			this.resetIdleCountdown();
		}

		this.startTimer();
	}
	
	triggerUserHasLeftPageOrGoneIdle() {
		if (this.isUserCurrentlyOnPage)
			this.isUserCurrentlyOnPage = false;

		this.stopTimer();
	}

	checkIdleState() {
		if (this.isUserCurrentlyIdle === false && this.currentIdleTimeMs > this.idleTimeoutMs) {
			this.isUserCurrentlyIdle = true;
			this.triggerUserHasLeftPageOrGoneIdle();
		} else
			this.currentIdleTimeMs += this.checkIdleStateRateMs;
	}

	listenEvents(trackIdWhenCopies, trackIdWhenViews) {
		// Setup check task copying
		let elem = document.getElementById(trackIdWhenCopies);
		if (elem !== undefined) {
			elem.addEventListener('copy', () => {
				this.user.task_copied = true;
			});
		}

		// Setup check task viewing
		let task_top_viewed = false;
		let task_bottom_viewed = false;
		let task_elem = document.getElementById(trackIdWhenViews);
		if (task_elem !== undefined) {
			let callback = () => {
				let bounding = task_elem.getBoundingClientRect();
				if (!task_top_viewed)
					task_top_viewed = bounding.top >= 0;
				
				if (!task_bottom_viewed)
					task_bottom_viewed = bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight);

				if (task_top_viewed && task_bottom_viewed)
					this.user.task_viewed = true;
			};

			callback();
			window.addEventListener('scroll', callback);
		}


		if (this.trackWhenUserLeavesPage)
			this.listenForUserLeavesOrReturnsEvents();

		if (this.trackWhenUserGoesIdle)
			this.listenForIdleEvents();

		// save data before unload
		window.addEventListener('beforeunload', () => {
			this.saveToStorage(JSON.stringify(this.getResult()));
		});

		// Setup send data each x seconds
		setInterval(() => {
			if (this.getTimeOnPageInMilliseconds() < this.delayBeforeSendMs)
				return;

			this.sendSafe(this.getResult(), (key, json) => {
				if (key === undefined)
					return;

				this.saveToStorage(json, key);
			});
		}, this.delayBeforeSendMs);
	}

	listenForUserLeavesOrReturnsEvents() {
		let visibilityChangeEventName = undefined;
		let hiddenPropName = undefined;

		if (typeof document.hidden !== "undefined") {
			this.hiddenPropName = "hidden";
			this.visibilityChangeEventName = "visibilitychange";
		} else if (typeof document.mozHidden !== "undefined") {
			this.hiddenPropName = "mozHidden";
			this.visibilityChangeEventName = "mozvisibilitychange";
		} else if (typeof document.msHidden !== "undefined") {
			this.hiddenPropName = "msHidden";
			this.visibilityChangeEventName = "msvisibilitychange";
		} else if (typeof document.webkitHidden !== "undefined") {
			this.hiddenPropName = "webkitHidden";
			this.visibilityChangeEventName = "webkitvisibilitychange";
		}

		document.addEventListener(this.visibilityChangeEventName, () => {
			if (document[this.hiddenPropName])
				this.triggerUserHasLeftPageOrGoneIdle();
			else
				this.triggerUserHasReturned();
		}, false);

		/*window.addEventListener('blur', () => {
			this.triggerUserHasLeftPageOrGoneIdle();
		});*/

		window.addEventListener('focus', () => {
			this.triggerUserHasReturned();
		});
	}

	listenForIdleEvents() {
		document.addEventListener("mousemove",  () => { this.userActivityDetected(); });
		document.addEventListener("keyup",      () => { this.userActivityDetected(); });
		document.addEventListener("touchstart", () => { this.userActivityDetected(); });
		window.addEventListener("scroll",       () => { this.userActivityDetected(); });

		setInterval(() => {
			if (this.isUserCurrentlyIdle !== true)
				this.checkIdleState();
		}, this.checkIdleStateRateMs);
	}

	getResult() {
		if (this.timer !== undefined) {
			this.stopTimer();
			this.startTimer();
		}

		let user = JSON.parse(this.getFromStorage());
		if (user === null) 
			user = Object.assign({}, this.user);
		else {
			this.removeFromStorage();

			user.reading_time += this.user.reading_time;
			user.task_copied = user.task_copied || this.user.task_copied;
			user.task_viewed = user.task_viewed || this.user.task_viewed;
		}

		user.reading_time += this.totalTime;

		this.totalTime = 0;
		this.user.reading_time = 0;
		this.user.task_copied = false;
		this.user.task_viewed = false;

		return user;
	}

	sendSafe(data, callback) {
		let json = JSON.stringify(data);

		$.post({
			url: this.host,
			dataType: 'json',
			contentType: 'application/json; charset=utf-8',
			data: json
		}).done(() => { callback() })
		  .fail(() => { callback(data.task_id, json) });
	}
};
