class Watcher {
	constructor(options) {
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
		this.websocketOptions = undefined;
		this.initialStartTime = undefined;

		let trackWhenUserLeavesPage = true;
		let trackWhenUserGoesIdle = true;

		if (options) {
			this.idleTimeoutMs = options.idleTimeoutInSeconds*1000 || this.idleTimeoutMs;
			this.currentPageName = options.currentPageName || this.currentPageName;
			this.websocketOptions = options.websocketOptions;
			this.initialStartTime = options.initialStartTime;

			if (options.trackWhenUserLeavesPage === false)
				trackWhenUserLeavesPage = false;

			if (options.trackWhenUserGoesIdle === false)
				trackWhenUserGoesIdle = false;
		}

		this.setIdleDurationInSeconds(this.idleTimeoutMs / 1000)
		this.setCurrentPageName(this.currentPageName)
		this.setUpWebsocket(this.websocketOptions)
		this.listenForVisibilityEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle);

		this.startTimer(undefined, this.initialStartTime);
	}

	trackTimeOnElement(elementId) {
		let element = document.getElementById(elementId);
		if (element) {
			element.addEventListener("mouseover", () => {
				this.startTimer(elementId);
			});
			element.addEventListener("mousemove", () => {
				this.startTimer(elementId);
			});
			element.addEventListener("mouseleave", () => {
				this.stopTimer(elementId);
			});
			element.addEventListener("keypress", () => {
				this.startTimer(elementId);
			});
			element.addEventListener("focus", () => {
				this.startTimer(elementId);
			});
		}
	}

	getTimeOnElementInSeconds(elementId) {
		let time = this.getTimeOnPageInSeconds(elementId);
		if (time)
			return time;
		else
			return 0;
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

	getTimeOnCurrentPageInSeconds() {
		return this.getTimeOnPageInSeconds(this.currentPageName);
	}

	getTimeOnPageInSeconds(pageName) {
		let timeInMs = this.getTimeOnPageInMilliseconds(pageName);
		if (timeInMs === undefined)
			return undefined;
		else
			return timeInMs / 1000;
	}

	getTimeOnCurrentPageInMilliseconds() {
		return this.getTimeOnPageInMilliseconds(this.currentPageName);
	}

	getTimeOnPageInMilliseconds(pageName) {
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

	getTimeOnAllPagesInSeconds() {
		let allTimes = [];
		let pageNames = Object.keys(this.startStopTimes);

		for (let i = 0; i < pageNames.length; i++) {
			let pageName = pageNames[i];
			let timeOnPage = this.getTimeOnPageInSeconds(pageName);

			allTimes.push({
				"pageName": pageName,
				"timeOnPage": timeOnPage
			});
		}

		return allTimes;
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

	resetRecordedPageTime(pageName) {
		delete this.startStopTimes[pageName];
	}

	resetAllRecordedPageTimes() {
		let pageNames = Object.keys(this.startStopTimes);

		for (let i = 0; i < pageNames.length; i++)
			this.resetRecordedPageTime(pageNames[i]);
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

	callWhenUserLeaves(callback, numberOfTimesToInvoke) {
		this.userLeftCallbacks.push({
			callback: callback,
			numberOfTimesToInvoke: numberOfTimesToInvoke
		});
	}

	callWhenUserReturns(callback, numberOfTimesToInvoke) {
		this.userReturnCallbacks.push({
			callback: callback,
			numberOfTimesToInvoke: numberOfTimesToInvoke
		});
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
	// TODO - we are muddying the waters in between
	// 'user left page' and 'user gone idle'. Really should be
	// two separate concepts entirely. Need to break this into smaller  functions
	// for either scenario.
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

	callAfterTimeElapsedInSeconds(timeInSeconds, callback) {
		this.timeElapsedCallbacks.push({
			timeInSeconds: timeInSeconds,
			callback: callback,
			pending: true
		});
	}

	checkIdleState() {
		for (let i = 0; i < this.timeElapsedCallbacks.length; i++) {
			if (this.timeElapsedCallbacks[i].pending && this.getTimeOnCurrentPageInSeconds() > this.timeElapsedCallbacks[i].timeInSeconds) {
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

	listenForVisibilityEvents(trackWhenUserLeavesPage, trackWhenUserGoesIdle) {
		if (trackWhenUserLeavesPage)
			this.listenForUserLeavesOrReturnsEvents();

		if (trackWhenUserGoesIdle)
			this.listForIdleEvents();
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

	listForIdleEvents() {
		document.addEventListener("mousemove", () => { this.userActivityDetected(); });
		document.addEventListener("keyup", () => { this.userActivityDetected(); });
		document.addEventListener("touchstart", () => { this.userActivityDetected(); });
		window.addEventListener("scroll", () => { this.userActivityDetected(); });

		setInterval(() => {
			if (this.isUserCurrentlyIdle !== true)
				this.checkIdleState();
		}, this.checkIdleStateRateMs);
	}

	setUpWebsocket(websocketOptions) {
		let websocket = undefined;
		let websocketHost = undefined;

		if (window.WebSocket && websocketOptions) {
			//let websocketHost = websocketOptions.websocketHost;
			//
			var url = "http://netx.ru/metric";
			let xhr = new XMLHttpRequest();
			xhr.open("PATCH", url);
			xhr.setRequestHeader("Accept", "application/json");
			xhr.setRequestHeader("Content-Type", "application/json");
			this.xhr = xhr;
			console.log('hello');

				alert();
			window.onbeforeunload = (e) => {
				alert();
				prompt();
				e.preventDefault();
				this.sendCurrentTime();
			};

			/*try {
				this.websocket = new WebSocket(websocketHost);

				window.onbeforeunload = () => {
					this.sendCurrentTime(websocketOptions.appId);
				};

				this.websocket.onopen = () => {
					this.sendInitWsRequest(websocketOptions.appId);
				};

				this.websocket.onerror = (error) => {
					if (console)
						console.log("Error occurred in websocket connection: " + error);
				};

				this.websocket.onmessage = (event) => {
					if (console)
						console.log(event.data);
				}
			} catch (error) {
				if (console) {
					console.error("Failed to connect to websocket host.  Error:" + error);
				}
			}*/
		}
	}

	sendCurrentTime(appId) {
		/*let timeSpentOnPage = this.getTimeOnCurrentPageInMilliseconds();
		let data = {
			type: "INSERT_TIME",
			appId: appId,
			timeOnPageMs: timeSpentOnPage,
			pageName: this.currentPageName
		};

		this.websocket.send(JSON.stringify(data));*/


		//xhr.setRequestHeader("Accept", "application/json");
		//xhr.setRequestHeader("Content-Type", "application/json");

		this.xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				console.log(xhr.status);
				console.log(xhr.responseText);
			}
		};

		var data = {
			'userId': 12345,
			'taskId': 666,
			'secondsOnPage': this.getTimeOnCurrentPageInMilliseconds() / 1000,
			'taskCopied': true
		};

		this.xhr.send(JSON.stringify(data));
	}

	sendInitWsRequest(appId) {
		return;
		let data = {
			type: "INIT",
			appId: appId
		};

		this.websocket.send(JSON.stringify(data));
	}	
};
