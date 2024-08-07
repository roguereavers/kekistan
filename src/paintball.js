const util = require("util");

const fontStyles = {
	default: "1em Arial",
}

const colors = {
	white: "#ccc",
	red: "#a00",
	yellow: "#dd0",
}

class Enemy extends util.Entity {
	constructor(ex, ey, options = {}) {
		super(ex * scale, ey * scale, scale / 1.25, scale / 1.25, options);

		this.type = "enemy";

		this.maxHealth = options.health || 1;
		this.health = options.health || 1;
		this.angle = util.toRad(options.rotate) || 0;
		this.patroling = true;
		
		if (options.path) {
			this.path = util.pathToPoints(options.path).map(p => ({ x: p.x * scale, y: p.y * scale }));
		} else {
			this.path = [new util.Point(ex * scale, ey * scale)];
		}

		this.pathdata = {
			index: 0,
			lastpos: this.path[0],
			newpos: this.path[1] || this.path[0],
		}

		this.on("shot", () => {
			this.health--;

			return this.health <= 0;
		});

		this.on("frame", () => {
			let vision;

			{ // vision cone
				let rayx = this.position.x + this.size.w / 2 + x;
				let rayy = this.position.y + this.size.h / 2 + y;
	
				vision = dishcast(rayx, rayy, this.angle, 200, undefined, this.id);

				drawDishcast(rayx, rayy, vision);
			}

			{ // detect player
				vision.forEach((ray) => {
					if (ray.target.type == "player") {
						detectedx = canvas.width / 2 - scale / 2.5 - x;
						detectedy = canvas.height / 2 - scale / 2.5 - y;
						isDetected = true;
					}
				});
			}

			if (isDetected) {
				this.angle = angle(this.position.x, this.position.y, detectedx, detectedy);
			} else if (this.patroling) {
				let p1 = this.pathdata.lastpos;
				let p2 = this.pathdata.newpos;

				if (!util.comparePoints(p1, p2)) {
					if (!util.comparePoints(this.position, p2)) {
						if (Math.sin(Math.round(util.toDeg(angle(p1.x, p1.y, p2.x, p2.y)))) != Math.sin(Math.round(util.toDeg(this.angle)))) {
							if (angle(p1.x, p1.y, p2.x, p2.y) < 0) {
								this.angle += util.toRad(-1.5);
							} else {
								this.angle += util.toRad(1.5);
							}
						} else {
							this.position.x += 2 * Math.cos(this.angle);
							this.position.y += 2 * Math.sin(this.angle);
						}
					} else {
						this.pathdata.index++;
						let i = this.pathdata.index;

						if (!this.path[i]) {
							this.pathdata.index = i = 0;
						}

						this.pathdata.lastpos = this.path[i];
						this.pathdata.newpos = this.path[i + 1] || this.path[0];
					}
				}
			}
		});
	}
}

class Door extends util.Entity {
	constructor(blockx, blocky, color, id, vertical = false, open = 0) {
		super(blockx * scale, blocky * scale, scale, scale, {
			label: "door",
			render: {
				shape: "custom",
				action: () =>
					drawDoor(blockx * scale + x, blocky * scale + y, this.open, this.color, this.vertical),
			},
		});

		this.id = id;

		this.color = color;

		this.vertical = vertical;

		this.open = open;
		this.opening = false;
		this.closing = false;

		this.on("collide", () => {
			if (this.open == 0) {
				return false;
			} else {
				return true;
			}
		});

		this.on("frame", () => {
			if (this.opening) {
				if (this.open < 1) {
					this.open += 0.05;
				} else {
					this.open = 1;
					this.opening = false;
				}
			}

			if (this.closing) {
				if (this.open > 0) {
					this.open -= 0.05;
				} else {
					this.open = 0;
					this.closing = false;
				}
			}
		});
	}
}

class Weapon {
	constructor(name, magammo, allammo, callback, interval = undefined) {
		this.name = name;
		this.callback = callback;

		this.currentmagammo = magammo;
		this.currentallammo = allammo;
		this.magammo = magammo;
		this.allammo = allammo;

		this.interval = interval;

		this.reloading = false;
	}

	shootBullet() {
		if (this.canShoot()) {
			this.currentmagammo--;
			spawn(this.callback());
		}

		if (this.canReload() && !this.canShoot()) {
			this.reload();
		}
	}

	shoot() {
		if (this.interval) {
			shooting = setInterval(() => this.shootBullet(), this.interval);
		} else {
			this.shootBullet();
		}
	}

	reload() {
		this.reloading = true;

		setTimeout(() => {
			this.currentmagammo = this.magammo;
			this.currentallammo -= this.magammo;
			this.reloading = false;
		}, 1000);
	}

	canShoot() {
		return this.currentmagammo > 0;
	}

	canReload() {
		return this.currentallammo > 0 && !this.reloading;
	}
}

class Bullet extends util.Entity {
	constructor(angle) {
		super(canvas.width / 2, canvas.height / 2, 5, 5, {
			label: "bullet",
			angle: angle,
			render: {
				color: colors[selectedColor[0]],
			},
		});

		this.on("frame", (e) => {
			e.position.x += 8 * Math.cos(e.angle);
			e.position.y += 8 * Math.sin(e.angle);

			let target = isColliding([new util.Point(e.position.x, e.position.y)]);
			
			if (target) {
				let ents = entities.filter(ent => ent != e);

				if (target.type) {
					switch (target.type) {
						case 10: case 11: case 12: {
							let newBlockID;

							if (selectedColor[0] == "white") newBlockID = 10;
							if (selectedColor[0] == "red") newBlockID = 11;
							if (selectedColor[0] == "yellow") newBlockID = 12;

							map[target.y][target.x] = newBlockID;
						} break;
					}
				} else {
					let dead = target.emit("shot", e);

					if (dead)
						ents = ents.filter(ent => ent != target);
				}

				return ents;
			}
		});
	}
}

let canvas = document.createElement("canvas");
canvas.width = document.children[0].scrollWidth;
canvas.height = document.children[0].scrollHeight;
document.body.appendChild(canvas);

// temporary data
let shooting;
let colorAnimating = false;
let colorFrame = 0;
let colorVel = 0;

// movement variables
let velx = 0;
let vely = 0;
let playerSpeed = 4;
let movforce = 0.3;
let movlt = false;
let movrt = false;
let movup = false;
let movdn = false;

// position variables
let x = 0;
let y = 0;
let lastx = x;
let lasty = y;
let detectedx = x;
let detectedy = y;
let isDetected = false;

// render option variables
let scale = 60;

// player variables
let selectedColor = ["white", "red", "yellow"]
let selectedWeapon = 0;
let weapons = [
	new Weapon("Pistol", 30, 240, () => {
		let bullet = new Bullet(angle(canvas.width / 2, canvas.height / 2, mouse.x, mouse.y));

		return bullet;
	}),
	new Weapon("Shotgun", 30, 240, () => {
		let bulletA = new Bullet(angle(canvas.width / 2, canvas.height / 2, mouse.x, mouse.y) - util.toRad(5));
		let bulletB = new Bullet(angle(canvas.width / 2, canvas.height / 2, mouse.x, mouse.y));
		let bulletC = new Bullet(angle(canvas.width / 2, canvas.height / 2, mouse.x, mouse.y) + util.toRad(5));

		return [bulletA, bulletB, bulletC];
	}),
	new Weapon("Rifle", 30, 240, () => {
		let bullet = new Bullet(angle(canvas.width / 2, canvas.height / 2, mouse.x, mouse.y));

		return bullet;
	}, 50),
]

// keyboard functions:
function keyboard_check(_key) { return key_down[_key]; }
function keyboard_check_pressed(_key) { return key_pressed[_key]; }
function keyboard_check_released(_key) { return key_released[_key]; }

// mouse functions:
function mouse_check() { return mouse_down; }
function mouse_check_pressed() { return mouse_pressed; }
function mouse_check_released() { return mouse_released; }

//virtual keys:
function key() {
	this.top = 0;
	this.left = 0;
	this.right = 0;
	this.bottom = 0;
	this.key = 0;
	this.down = false;
	this.active = true;
}
// mouse object
let mouse = new util.Point(0, 0);
document.addEventListener("mousemove", (e) => {
	mouse.x = e.clientX;
	mouse.y = e.clientY;
});

function key_add(_x, _y, _w, _h, _k) {
	var _v = new vkey();
	_v.left = _x;
	_v.top = _y;
	_v.right = _x + _w;
	_v.bottom = _y + _h;
	_v.width = _w;
	_v.height = _h;
	_v.key = _k;
	tu_vkeys.push(_v);
	return _v;
}
// misc:
function trace() { console.log.apply(console, arguments); }
function idle() { } // left empty on purpose

// map variables
// 0  air
// 1  wall
// 5  spawnpoint
// 6  finish
// 10 white wool
// 11 red wool
// 12 yellow wool
let levels = [
	{
		behavior: [
			"if 2 6 == 11 > open door > close door",
		],
		map: [
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
			[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
			[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
			[1, 0, 0, 0, 1, 0, 5, 0, 1, 0, 0, 0, 1],
			[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
			[1, 0, 10, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1],
			[1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		],
		entities: [
			new Enemy(2, 2, { health: 10, rotate: 90, path: ["2 2", "2 4"] }),
			new Enemy(10, 6, { health: 10, rotate: -90, path: ["10 6", "10 2"] }),
			new Door(12, 7, "red", "door", true),
		],
	},
	{
		map: [
			[1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 5, 0, 0, 0, 6, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 1, 1, 1, 1, 1, 1, 1],
		],
	},
	{
		behavior: [
			"if 6 2 == 11 > open door > close door",
		],
		map: [
			[1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 5, 0, 0, 0, 10, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 0, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 1],
			[1, 0, 6, 0, 1],
			[1, 0, 0, 0, 1],
			[1, 1, 1, 1, 1],
		],
		entities: [
			new Door(2, 4, "red", "door"),
		],
	},
]

let currentMap = 0;

let behavior = [];
let map = [];
let entities = [];

selectMap(0);

{ // controls
	document.addEventListener("keydown", (e) => {
		switch (e.code) {
			case "KeyW": movup = true; break;
			case "KeyS": movdn = true; break;
			case "KeyA": movlt = true; break;
			case "KeyD": movrt = true; break;

			case "KeyK": selectMap(currentMap); break;

			case "KeyR": {
				let weapon = weapons[selectedWeapon];

				if (weapon.canReload())
					weapon.reload();
			} break;

			case "Digit1": selectWeapon(0); break;
			case "Digit2": selectWeapon(1); break;
			case "Digit3": selectWeapon(2); break;
		}
	});

	document.addEventListener("keyup", (e) => {
		switch (e.code) {
			case "KeyW": movup = false; break;
			case "KeyS": movdn = false; break;
			case "KeyA": movlt = false; break;
			case "KeyD": movrt = false; break;
		}
	});

	document.addEventListener("mousedown", (e) => {
		if (e.button == 0) {
			weapons[selectedWeapon].shoot();
		} else if (e.button == 2) {
			if (!colorAnimating) {
				colorVel = 0.15;
				colorAnimating = true;
			} else {
				colorVel = 2;
			}
		}
	});

	document.addEventListener("mouseup", (e) => {
		if (e.button == 0) {
			clearInterval(shooting);
		} else if (e.button == 2) {
			// smth
		}
	});
}

// load resources
let asseturls = ["img/finish.png", "img/white-wool.png", "img/red-wool.png", "img/yellow-wool.png"]
let assetsImported = 0;
let assets = {}

{ // get assets
	asseturls.forEach((a) => {
		let path = "./src/" + a;
		let loader = assets[path.split("/").pop()] = new Image();

		loader.src = path;

		loader.addEventListener("load", () => {
			assetsImported++;

			if (assetsImported == asseturls.length)
				frame();
		});
	});
}

// rendering and physics
let ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;
ctx.font = fontStyles.default;
ctx.lineWidth = 2;

function frame() {
	window.requestAnimationFrame(frame);

	ctx.fillStyle = "#161621";
	ctx.fillRect(0, 0, canvas.width, canvas.height);

	{ // calculate player movement
		velx += movlt ? movforce : -movforce;
		velx += movrt ? -movforce : movforce;
		vely += movup ? movforce : -movforce;
		vely += movdn ? -movforce : movforce;

		if (velx > playerSpeed) velx = playerSpeed;
		if (velx < -playerSpeed) velx = -playerSpeed;
		if (vely > playerSpeed) vely = playerSpeed;
		if (vely < -playerSpeed) vely = -playerSpeed;

		velx = Math.round(velx * 10) / 10;
		vely = Math.round(vely * 10) / 10;

		if (!movlt && !movrt && velx != 0) {
			if (velx < 0)
				velx += movforce;
			
			if (velx > 0)
				velx -= movforce;
		}

		if (!movup && !movdn && vely != 0) {
			if (vely < 0)
				vely += movforce;

			if (vely > 0)
				vely -= movforce;
		}

		lastx = x;
		lasty = y;
		let cpoints = [
			new util.Point(canvas.width / 2 - scale / 2.5, canvas.height / 2 - scale / 2.5),
			new util.Point(canvas.width / 2 + scale / 2.5, canvas.height / 2 - scale / 2.5),
			new util.Point(canvas.width / 2 - scale / 2.5, canvas.height / 2 + scale / 2.5),
			new util.Point(canvas.width / 2 + scale / 2.5, canvas.height / 2 + scale / 2.5),
		];

		{ // x movement
			x = Math.round(x + velx);

			if (isColliding(cpoints, true))
				x -= Math.round(velx);
		}

		{ // y movement
			y = Math.round(y + vely);

			if (isColliding(cpoints, true))
				y -= Math.round(vely);
		}
	}

	{ // calculate entity movement
		let ents = entities;

		for (let i = 0; i < entities.length; i++) {
			let e = entities[i];

			let newents = e.emit("frame", e);

			if (newents)
				ents = newents;
		}
		
		entities = ents;
	}

	{ // evaluate map behavior
		let parseLine = (line) => {
			let tokens = line.split(" ");

			switch (tokens[0]) {
				case "if": {
					let parts = line.split(" > ");

					let condition = parts[0].split(" ");
					condition.shift();

					let result = false;

					switch (condition[2]) {
						case "==": {
							result =
								map[parseInt(condition[1])][parseInt(condition[0])] == parseInt(condition[3]);
						} break;
					}

					if (result) {
						parseLine(parts[1]);
					} else {
						parseLine(parts[2]);
					}
				} break;

				case "set": {
					map[parseInt(tokens[2])][parseInt(tokens[1])] = parseInt(tokens[3]);
				} break;

				case "close": {
					entities.forEach((e) => {
						if (e.id == tokens[1]) {
							e.closing = true;
						}
					});
				} break;

				case "open": {
					entities.forEach((e) => {
						if (e.id == tokens[1]) {
							e.opening = true;
						}
					});
				} break;

				case "jump": {
					i = parseInt(tokens[1]) - 1;
				} break;

				case "continue": break;

				default: {
					console.error(`Invalid Behavior Token: "${tokens[0]}" on line "${line}".`);
				}
			}
		}

		let i = 0;

		for (; i < behavior.length; i++) {
			parseLine(behavior[i]);
		}
	}

	{ // show map
		for (let i = 0; i < map.length; i++) {
			for (let j = 0; j < map[i].length; j++) {
				let blocktype = map[i][j];

				let blockx = j * scale + x;
				let blocky = i * scale + y;

				switch (blocktype) {
					case 1: {
						ctx.fillStyle = "#aaa";
						ctx.fillRect(blockx, blocky, scale, scale);
					} break;

					case 5: {
						ctx.fillStyle = "#0a0";
						ctx.fillRect(blockx, blocky, scale, scale);
					} break;

					case 6: {
						ctx.drawImage(assets["finish.png"], blockx, blocky, scale, scale);
					} break;

					case 10: {
						ctx.drawImage(assets["white-wool.png"], blockx, blocky, scale, scale);
					} break;

					case 11: {
						ctx.drawImage(assets["red-wool.png"], blockx, blocky, scale, scale);
					} break;

					case 12: {
						ctx.drawImage(assets["yellow-wool.png"], blockx, blocky, scale, scale);
					} break;
				}
			}
		}
	}

	{ // show entities
		entities.forEach((e) => {
			switch (e.render.shape) {
				case "circle": {
					ctx.beginPath();

					if (e.label != "bullet")
						ctx.ellipse(e.position.x + e.size.w / 2 + x, e.position.y + e.size.h / 2 + y, e.size.w / 2, e.size.h / 2, 0, 0, Math.PI * 2);
					if (e.label == "bullet")
						ctx.ellipse(e.position.x, e.position.y, e.size.w / 2, e.size.h / 2, 0, 0, Math.PI * 2);

					ctx.fillStyle = e.render.color;
					ctx.fill();
				} break;

				case "custom": {
					e.render.action();
				} break;
			}

			if (e.label != "bullet" && e.maxHealth != e.health) {
				ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
				ctx.fillRect(e.position.x + x, e.position.y + y - em(0.8), e.size.w, em(0.5));

				ctx.fillStyle = "rgba(0, 255, 0, 0.3)";
				ctx.fillRect(e.position.x + x, e.position.y + y - em(0.8), (e.size.w / e.maxHealth) * e.health, em(0.5));
			}
		});
	}

	{ // display weapon info
		{ // weapon display
			let skip = em(1.5);
			let xskip = em(1.5);
	
			weapons.forEach((w, i) => {
				if (i == selectedWeapon) {
					ctx.fillStyle = "#ddd";
					ctx.fillRect(xskip, skip, 240, em(4));
	
					ctx.fillStyle = "#161621";
					ctx.fillText(`${w.name} ${w.reloading ? "(Reloading)" : ""}`,
						xskip + em(0.5), skip + em(1.4));
					ctx.fillText(`${w.currentmagammo} / ${w.currentallammo}`,
						xskip + em(0.5), skip + em(3.4));
	
					skip += em(4);
				} else {
					ctx.fillStyle = "#ddd";
					ctx.fillText(`${w.name} (${w.currentmagammo} / ${w.currentallammo}) ${w.reloading ? "(Reloading)" : ""}`,
						xskip + em(0.5), skip + em(1.4));
	
					skip += em(2);
				}
			});
		}

		{ // selected color
			if (colorAnimating) {
				colorVel -= 0.005;
				colorFrame += colorVel;

				if (colorFrame >= 2) {
					colorFrame = 0;
					colorAnimating = false;
					selectedColor.push(selectedColor.shift());
				}
			}

			ctx.strokeStyle = "#000";

			ctx.fillStyle = colors[selectedColor[2]];
			ctx.beginPath();
			ctx.ellipse(canvas.width - em(2 + colorFrame), em(4 - colorFrame), em(), em(), 0, 0, Math.PI * 2);
			ctx.fill(); ctx.stroke();

			ctx.fillStyle = colors[selectedColor[1]];
			ctx.beginPath();
			ctx.ellipse(canvas.width - em(4), em(2 + colorFrame), em(1 + colorFrame / 2), em(1 + colorFrame / 2), 0, 0, Math.PI * 2);
			ctx.fill(); ctx.stroke();

			ctx.fillStyle = colors[selectedColor[0]];
			ctx.beginPath();
			ctx.ellipse(canvas.width - em(4 - colorFrame), em(4), em(2 - colorFrame / 2), em(2 - colorFrame / 2), 0, 0, Math.PI * 2);
			ctx.fill(); ctx.stroke();
		}
	}

	// show player
	ctx.fillStyle = "#ddd";
	ctx.beginPath();
	ctx.ellipse(canvas.width / 2, canvas.height / 2, scale / 2.5, scale / 2.5, 0, 0, Math.PI * 2);
	ctx.closePath();
	ctx.fill();
}

// minimal math:
function abs(_value) { return _value < 0 ? -_value : _value; }
function sign(_value) { return _value > 0 ? 1 : _value < 0 ? -1 : 0; }
function choose() { return arguments[~~(Math.random() * arguments.length)]; }
function random(_value) { return Math.random() * _value; }
function irandom(_value) { return ~~(Math.random() * _value + 1); }
// trig functions:
function lengthdir_x(_length, _direction) { return _length * Math.cos(_direction * tu_d2r); }
function lengthdir_y(_length, _direction) { return _length * Math.sin(_direction * tu_d2r); }
function point_distance(_x1, _y1, _x2, _y2) { return Math.sqrt(Math.pow(( _x1 - _x2), 2) + Math.pow((_y1 - _y2), 2)); }
function point_direction(_x1, _y1, _x2, _y2) { return Math.atan2(_y2 - _y1, _x2 - _x1) * tu_r2d; }
function degtorad(_degree) { return _degree * d2r; }
function radtodeg(_degree) { return _degree * r2d; }

function isColliding(points, player = false, ignore = -1, collidesWithPlayer = false) {
	if (collidesWithPlayer) {
		let colliding = false;

		let playerx = canvas.width / 2 - scale / 2.5;
		let playery = canvas.height / 2 - scale / 2.5;

		points.forEach((p) => {
			if ((p.x >= playerx && p.x <= playerx + scale / 1.25) &&
			    (p.y >= playery && p.y <= playery + scale / 1.25)) {
				colliding = true;
			}
		});

		if (colliding)
			return { type: "player" };
	}

	for (let i = 0; i < map.length; i++) {
		for (let j = 0; j < map[i].length; j++) {
			let blocktype = map[i][j];

			let blockx = j * scale + x;
			let blocky = i * scale + y;

			let colliding = false;

			points.forEach((p) => {
				if ((p.x >= blockx && p.x <= blockx + scale) &&
					(p.y >= blocky && p.y <= blocky + scale)) {
					colliding = true;
				}
			});

			if (colliding) {
				switch(blocktype) {
					case 1: case 10: case 11: case 12: {
						return { x: j, y: i, type: blocktype }
					} break;

					case 6: {
						if (player)
							selectMap(currentMap + 1);
					} break;
				}
			}
		}
	}

	for (let i = 0; i < entities.length; i++) {
		let e = entities[i];

		let colliding = false;

		points.forEach((p) => {
			if ((p.x >= e.position.x + x && p.x <= e.position.x + e.size.w + x) &&
				(p.y >= e.position.y + y && p.y <= e.position.y + e.size.h + y)) {
				colliding = !e.emit("collide");
			}
		});

		if (colliding && e.id !== ignore)
			return e;
	}
}

// instance collision checking:
function instance_position(_px, _py, _object, _mult) {
	var _x, _y, _ox, _oy, _sx, _sy, _o, _s, _i, _il, _r, _dx, _dy,
		_q = (_object.__instance ? [_object] : instance_list(_object)),
		_tm = (_mult) ? true : false;
	if (_tm) _ta = [];
	_il = _q.length;
	for (_i = 0; _i < _il; _i++) {
		_o = _q[_i];
		if (!_o.collision_checking) continue;
		_s = _o.sprite_index;
		if (!_s) continue;
		_x = _o.x; _sx = _o.image_xscale;
		_y = _o.y; _sy = _o.image_yscale;
		switch (_s.collision_shape)
		{
		case 0x2:
			if (_sx == 1 && _sy == 1) {
				_ox = _s.xoffset; _oy = _s.yoffset;
				if (!collide_bbox_point(_x + _s.collision_left - _ox, _y + _s.collision_top - _oy,
				_x + _s.collision_right - _ox, _y + _s.collision_bottom - _oy, _px, _py)) break;
			} else if (!collide_sbox_point(_x, _y, _sx, _sy, _s)) break;
			if (!_tm) return _o;
			_ta.push(_o);
			break;
		case 0x3:
			_r = _s.collision_radius * Math.max(_o.image_xscale, _o.image_yscale);
			_dx = _o.x + (_s.width / 2 - _s.xoffset) - _px;
			_dy = _o.y + (_s.height / 2 - _s.yoffset) - _py;
			if ((_dx * _dx) + (_dy * _dy) > _r * _r) break;
			if (!_tm) return _o;
			_ta.push(_o);
			break;
		}
	}
	return _tm ? _ta : null;
}


function selectMap(id) {
	currentMap = id;

	let lvl = levels[id];

	behavior = lvl.behavior || [];
	map = lvl.map || [];
	entities = lvl.entities || [];
	
	{ // initialize
		{ // map ignition
			for (let i = 0; i < map.length; i++) {
				for (let j = 0; j < map[i].length; j++) {
					let blockx = j * scale;
					let blocky = i * scale;
	
					switch (map[i][j]) {
						case 5: {
							x = canvas.width / 2 - blockx - scale / 2;
							y = canvas.height / 2 - blocky - scale / 2;
						} break;

						case 3: {

						} break;
					}
				}
			}
		}
	}
}

function spawn(e) {
	if (e[0]) {
		e.forEach(ent => entities.push(ent));
	} else {
		entities.push(e);
	}
}

function drawDoor(startx, starty, open, color = "white", vertical = false) {
	let x;
	let y ;

	let bit = scale / 10;

	if (vertical) {
		x = startx;
		y = Math.round(starty - open * (scale / 2));

		{ // draw door first half
			ctx.fillStyle = "#aaa";

			ctx.beginPath();
			ctx.moveTo(x, y);
			ctx.lineTo(x + scale, y);
			ctx.lineTo(x + scale, y + bit * 4);
			ctx.lineTo(x + scale - bit, y + bit * 5);
			ctx.lineTo(x + bit, y + bit * 5);
			ctx.lineTo(x, y + bit * 4);
			ctx.lineTo(x, y);
			ctx.fill();
		}

		{ // draw color first half
			ctx.fillStyle = colors[color];

			ctx.beginPath();
			ctx.ellipse(x + scale / 2, y + scale / 2, scale / 6, scale / 6, Math.PI, 0, Math.PI);
			ctx.fill();
		}

		y = Math.round(starty + open * (scale / 2));

		{ // draw door second half
			ctx.fillStyle = "#aaa";

			ctx.beginPath();
			ctx.moveTo(x, y + scale / 2);
			ctx.lineTo(x + bit * 9, y + scale / 2);
			ctx.lineTo(x + scale, y + bit + scale / 2);
			ctx.lineTo(x + scale, y + scale);
			ctx.lineTo(x, y + scale);
			ctx.lineTo(x, y + bit * 6);
			ctx.lineTo(x + bit, y + scale / 2);
			ctx.fill();
		}

		{ // draw color second half
			ctx.fillStyle = colors[color];

			ctx.beginPath();
			ctx.ellipse(x + scale / 2, y + scale / 2, scale / 6, scale / 6, 0, 0, Math.PI);
			ctx.fill();
		}

		y = Math.round(startx + open * (scale / 2));
	} else {
		y = starty;
		x = Math.round(startx - open * (scale / 2));
		
		{ // draw door first half
			ctx.fillStyle = "#aaa";

			ctx.beginPath();
			ctx.moveTo(x, y);
			ctx.lineTo(x + bit * 4, y);
			ctx.lineTo(x + bit * 5, y + bit);
			ctx.lineTo(x + bit * 5, y + scale - bit);
			ctx.lineTo(x + bit * 4, y + scale);
			ctx.lineTo(x, y + scale);
			ctx.lineTo(x, y);
			ctx.fill();
		}
		
		{ // draw color first half
			ctx.fillStyle = colors[color]
			
			ctx.beginPath();
			ctx.ellipse(x + scale / 2, y + scale / 2, scale / 6, scale / 6, util.toRad(90), 0, Math.PI);
			ctx.fill();
		}
		
		x = Math.round(startx + open * (scale / 2));
		
		{ // draw door second half
			ctx.fillStyle = "#aaa";
			
			ctx.beginPath();
			ctx.moveTo(x, y);
			ctx.lineTo(x + bit * 6, y);
			ctx.lineTo(x + scale, y);
			ctx.lineTo(x + scale, y + scale);
			ctx.lineTo(x + bit * 6, y + scale);
			ctx.lineTo(x + bit * 5, y + scale - bit);
			ctx.lineTo(x + bit * 5, y + bit);
			ctx.lineTo(x + bit * 6, y);
			ctx.fill();
		}
		
		{ // draw color second half
			ctx.fillStyle = colors[color]
			
			ctx.beginPath();
			ctx.ellipse(x + scale / 2, y + scale / 2, scale / 6, scale / 6, util.toRad(-90), 0, Math.PI);
			ctx.fill();
		}
	}
}

function drawDishcast(x, y, rays) {
	ctx.beginPath();
	ctx.moveTo(x, y);

	rays.forEach((ray) => {
		ctx.lineTo(ray.x, ray.y);
	});

	ctx.lineTo(x, y);

	ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
	ctx.fill();
}

function dishcast(x, y, angle, maxdist, resolution, ignore) {
	let rays = [];

	for (let i = 10; i > 0; i--) {
		rays.push(raycast(x, y, angle - util.toRad(5 * i), maxdist, resolution, ignore));
	}

	for (let i = 1; i < 11; i++) {
		rays.push(raycast(x, y, angle + util.toRad(5 * i), maxdist, resolution, ignore));
	}

	return rays;
}

function raycast(x, y, angle, maxdist = 100, resolution = 23, ignore = -1) {
	let pos = new util.Point(x, y);
	let target;

	while (!target) {
		pos.x += resolution * Math.cos(angle);
		pos.y += resolution * Math.sin(angle);

		target = isColliding([pos], false, ignore, true);

		if (distance(x, y, pos.x, pos.y) > maxdist) {
			target = "maxdist";
			break;
		}
	}

	return { x: pos.x, y: pos.y, target: target }
}

function angle(cx, cy, ex, ey) {
	return Math.atan2(ey - cy, ex - cx);
}

function distance(cx, cy, ex, ey) {
	let a = cx - ex;
	let b = cy - ey;

	return Math.sqrt(a * a + b * b);
}

function em(x = 1) {
	return x * parseFloat(getComputedStyle(document.body).fontSize);
}

function selectWeapon(id) {
	selectedWeapon = id;
}

/ web data:
function save_web_data(_name, _value) { if (window.localStorage) window.localStorage.setItem(_name, _value); }
function save_web_integer(_name, _value) { if (window.localStorage) window.localStorage.setItem("int_" + _name, _value); }
function save_web_float(_name, _value) { if (window.localStorage) window.localStorage.setItem("float_" + _name, _value); }
function save_web_string(_name, _value) { if (window.localStorage) window.localStorage.setItem("string_" + _name, _value); }
function load_web_data(_name) { if (window.localStorage) return window.localStorage.getItem(_name); }
function load_web_integer(_name) { if (window.localStorage) return parseInt(window.localStorage.getItem("int_" + _name)); }
function load_web_float(_name) { if (window.localStorage) return parseFloat(window.localStorage.getItem("float_" + _name)); }
function load_web_string(_name) { if (window.localStorage) return '' + window.localStorage.getItem("string_" + _name); }
function delete_web_data(_name) { if (window.localStorage) window.localStorage.removeItem(_name); }
function delete_web_integer(_name) { if (window.localStorage) window.localStorage.removeItem("int_" + _name); }
function delete_web_float(_name) { if (window.localStorage) window.localStorage.removeItem("float_" + _name); }
function delete_web_string(_name) { if (window.localStorage) window.localStorage.removeItem("string_" + _name); }
function clear_web_data() { if (window.localStorage) window.localStorage.clear(); }
function web_data_number() { if (window.localStorage) return window.localStorage.length; }