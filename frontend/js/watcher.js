class Watcher {
	constructor(host, options) {
		this.host = host;
		this.timer = undefined;
		this.timeOnPage = 0;
		this.idleTimeoutMs = 30 * 1000;
		this.currentIdleTimeMs = 0;
		this.checkIdleStateRateMs = 250;
		this.isUserCurrentlyOnPage = true;
		this.isUserCurrentlyIdle = false;
		this.currentPageName = "default-page-name";
		this.initialStartTime = undefined;

		this.idWasCopied = false;
		let trackWhenUserLeavesPage = true;
		let trackWhenUserGoesIdle = true;

		if (options) {
			this.idleTimeoutMs = options.idleTimeoutInSeconds*1000 || this.idleTimeoutMs;
			this.currentPageName = options.currentPageName || this.currentPageName;
			this.initialStartTime = options.initialStartTime;

			if (options.trackWhenUserLeavesPage === false)
				trackWhenUserLeavesPage = false;

			if (options.trackWhenUserGoesIdle === false)
				trackWhenUserGoesIdle = false;
		}

		this.listenEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle, options.trackIdWhenCopies);
		this.startTimer(this.initialStartTime);
	}

	startTimer(startTime) {
		if (this.timer !== undefined && this.timer.stopTime === undefined)
			return;
		else if (this.timer !== undefined)
			this.timeOnPage += Number(this.timer.stopTime - this.timer.startTime);

		this.timer = {
			'startTime': startTime || new Date(),
			'stopTime': undefined
		};
	}

	stopTimer(stopTime) {
		if (this.timer === undefined)
			return;

		if (this.timer.stopTime === undefined)
			this.timer.stopTime = stopTime || new Date();
	}

	getTimeOnPageInMilliseconds() {
		let diff = 0;

		if (this.timer !== undefined) {
			let startTime = this.timer.startTime;
			let stopTime = this.timer.stopTime || new Date();
			diff = Number(stopTime - startTime);
		}

		return this.timeOnPage + diff;
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

	listenEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle, trackIdWhenCopies) {
		if (trackWhenUserLeavesPage)
			this.listenForUserLeavesOrReturnsEvents();

		if (trackWhenUserGoesIdle)
			this.listenForIdleEvents();

		if (trackIdWhenCopies) {
			let elem = document.getElementById(trackIdWhenCopies);
			if (elem === undefined)
				return;

			elem.addEventListener('copy', (e) => {
				this.idWasCopied = true;
			});
		}

		// Setup connection
		//window.addEventListener('pagehide', () => {this.sendCurrentTime()});
		//window.addEventListener('beforeunload', () => {this.sendCurrentTime()});

		$(window).on('beforeunload', () => {this.sendCurrentTime()});
		//$(window).on('unload', () => {this.sendCurrentTime()});

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

		window.addEventListener('blur', () => {
			this.triggerUserHasLeftPageOrGoneIdle();
		});

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

	sendCurrentTime() {
		const data = JSON.stringify({
			userId: 12345,
			taskId: 666,
			secondsOnPage: this.getTimeOnPageInMilliseconds() / 1000,
			taskCopied: this.idWasCopied
		});

		if (navigator.sendBeacon)
			navigator.sendBeacon(this.host, new Blob([data], {type: 'application/json'}));
		else {
			/*let xhr = new XMLHttpRequest();
			xhr.open("POST", this.host);
			xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
			xhr.onopen = () => {xhr.send(data)};*/

			$.post({
				url: this.host,
				dataType: 'json',
				contentType: 'application/json; charset=utf-8',
				data: data,
				success: () => {}
			});
		}
	}
};
