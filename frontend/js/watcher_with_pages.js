class Watcher {
	constructor(host, options) {
		this.startStopTimes = {};
		this.idleTimeoutMs = 30 * 1000;
		this.currentIdleTimeMs = 0;
		this.checkIdleStateRateMs = 250;
		this.isUserCurrentlyOnPage = true;
		this.isUserCurrentlyIdle = false;
		this.currentPageName = "default-page-name";
		this.timeElapsedCallbacks = [];
		this.userLeftCallbacks = []
		this.userReturnCallbacks = [];
		this.initialStartTime = undefined;

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

		this.setUpConnection(host);

		this.setIdleDurationInSeconds(this.idleTimeoutMs / 1000);
		this.setCurrentPageName(this.currentPageName);
		this.listenEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle);

		this.startTimer(this.currentPageName, this.initialStartTime);
	}

	startTimer(pageName, startTime) {
		if (!pageName)
			pageName = this.currentPageName;

		if (this.startStopTimes[pageName] === undefined)
			this.startStopTimes[pageName] = [];
		else {
			let arrayOfTimes = this.startStopTimes[pageName];
			let latestStartStopEntry = arrayOfTimes[arrayOfTimes.length - 1];
			if (latestStartStopEntry !== undefined && latestStartStopEntry.stopTime === undefined)
				return;
		}

		this.startStopTimes[pageName].push({
			"startTime": startTime || new Date(),
			"stopTime": undefined
		});
	}

	stopAllTimers() {
		let pageNames = Object.keys(this.startStopTimes);
		for (let i = 0; i < pageNames.length; i++)
			this.stopTimer(pageNames[i]);
	}

	stopTimer(pageName, stopTime) {
		if (!pageName) 
			pageName = this.currentPageName;

		let arrayOfTimes = this.startStopTimes[pageName];
		if (arrayOfTimes === undefined || arrayOfTimes.length === 0)
			return;

		if (arrayOfTimes[arrayOfTimes.length - 1].stopTime === undefined)
			arrayOfTimes[arrayOfTimes.length - 1].stopTime = stopTime || new Date();
	}

	getTimeOnPageInSeconds(pageName) {
		let timeInMs = this.getTimeOnPageInMilliseconds(pageName);
		if (timeInMs === undefined)
			return undefined;
		else
			return timeInMs / 1000;
	}

	getTimeOnPageInMilliseconds(pageName) {
		if (!pageName)
			pageName = this.currentPageName;

		let totalTimeOnPage = 0;

		let arrayOfTimes = this.startStopTimes[pageName];
		if (arrayOfTimes === undefined)
			return;

		let timeSpentOnPageInSeconds = 0;
		for (let i = 0; i < arrayOfTimes.length; i++) {
			let startTime = arrayOfTimes[i].startTime;
			let stopTime = arrayOfTimes[i].stopTime;
			if (stopTime === undefined)
				stopTime = new Date();

			let difference = stopTime - startTime;
			timeSpentOnPageInSeconds += (difference);
		}

		totalTimeOnPage = Number(timeSpentOnPageInSeconds);
		return totalTimeOnPage;
	}

	setIdleDurationInSeconds(duration) {
		let durationFloat = parseFloat(duration);

		if (isNaN(durationFloat) === false)
			this.idleTimeoutMs = duration * 1000;
		else {
			throw {
				name: "InvalidDurationException",
				message: "An invalid duration time (" + duration + ") was provided."
			};
		}
	}

	setCurrentPageName(pageName) {
		this.currentPageName = pageName;
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

			for (let i = 0; i < this.userReturnCallbacks.length; i++) {
				let userReturnedCallback = this.userReturnCallbacks[i];
				let numberTimes = userReturnedCallback.numberOfTimesToInvoke;

				if (isNaN(numberTimes) || (numberTimes === undefined) || numberTimes > 0) {
					userReturnedCallback.numberOfTimesToInvoke -= 1;
					userReturnedCallback.callback();
				}
			}
		}

		this.startTimer();
	}
	
	triggerUserHasLeftPageOrGoneIdle() {
		if (this.isUserCurrentlyOnPage) {
			this.isUserCurrentlyOnPage = false;

			for (let i = 0; i < this.userLeftCallbacks.length; i++) {
				let userHasLeftCallback = this.userLeftCallbacks[i];
				let numberTimes = userHasLeftCallback.numberOfTimesToInvoke;

				if (isNaN(numberTimes) || (numberTimes === undefined) || numberTimes > 0) {
					userHasLeftCallback.numberOfTimesToInvoke -= 1;
					userHasLeftCallback.callback();
				}
			}
		}

		this.stopAllTimers();
	}

	checkIdleState() {
		for (let i = 0; i < this.timeElapsedCallbacks.length; i++) {
			if (this.timeElapsedCallbacks[i].pending && this.getTimeOnPageInSeconds() > this.timeElapsedCallbacks[i].timeInSeconds) {
				this.timeElapsedCallbacks[i].callback();
				this.timeElapsedCallbacks[i].pending = false;
			}
		}

		if (this.isUserCurrentlyIdle === false && this.currentIdleTimeMs > this.idleTimeoutMs) {
			this.isUserCurrentlyIdle = true;
			this.triggerUserHasLeftPageOrGoneIdle();
		} else
			this.currentIdleTimeMs += this.checkIdleStateRateMs;
	}

	listenEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle) {
		if (trackWhenUserLeavesPage)
			this.listenForUserLeavesOrReturnsEvents();

		if (trackWhenUserGoesIdle)
			this.listenForIdleEvents();
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
		document.addEventListener("mousemove", () => { this.userActivityDetected(); });
		document.addEventListener("keyup", () => { this.userActivityDetected(); });
		document.addEventListener("touchstart", () => { this.userActivityDetected(); });
		window.addEventListener("scroll", () => { this.userActivityDetected(); });

		setInterval(() => {
			if (this.isUserCurrentlyIdle !== true)
				this.checkIdleState();
		}, this.checkIdleStateRateMs);
	}

	setUpConnection(host) {
		this.host = host;

		//window.addEventListener('pagehide', () => {this.sendCurrentTime()});
		//window.addEventListener('beforeunload', () => {this.sendCurrentTime()});

		$(window).on('beforeunload', () => {this.sendCurrentTime()});
		//$(window).on('unload', () => {this.sendCurrentTime()});
	}

	sendCurrentTime() {
		const data = JSON.stringify({
			'userId': 12345,
			'taskId': 666,
			'secondsOnPage': this.getTimeOnPageInSeconds(),
			'taskCopied': true
		});

		if (navigator.sendBeacon) {
			navigator.sendBeacon(this.host, new Blob([data], {type: 'application/json'}));
		} else {
			/*let xhr = new XMLHttpRequest();
			xhr.open("POST", host);
			xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
			xhr.onopen = () => {xhr.send(data)};*/

			$.post({
				url: '/metric',
				dataType: 'json',
				contentType: 'application/json; charset=utf-8',
				data: data,
				success: () => {}
			});
		}
	}
};
