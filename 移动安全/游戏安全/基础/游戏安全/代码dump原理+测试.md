# dump原理
## 环境
Virtual app

## 原理简介

Cocos引擎的lua加载器为cocos2dx_lua_loader , 其中使用luaL_loadbuffer,lual_loadbuffer()中的参数含有lua源码，hook这个函数以后就可以dump出源码。

```
    if (strstr(name, "libgame.so") != NULL && Count != true) {
        MYLOGD("onSoLoaded==>%s", name);
        void *xluaL_loadbuffer = (void *) dlsym(handle, "luaL_loadbufferx");
        MYLOGD("onSoLoaded=> xluaL_loadbuffer:%p", xluaL_loadbuffer);
        if (xluaL_loadbuffer != NULL) {
            MSHookFunction((void *) xluaL_loadbuffer, (void *) new_xluaL_loadbuffer,
                           (void **) &old_xluaL_loadbuffer);
            Count = true;
        }

    }
```
替换的函数
```
int  new_xluaL_loadbuffer(lua_State *L, const char *buff, size_t sz, const char *name,const char *mode) {

    char mypath[256] = {0};
    char dstpath[256] = {0};
    char *dirname01 = strdup(name); //strdup()
    char *basename01 = strdup(name);
    char *dname = dirname(dirname01);
    char *bname = basename(basename01);
    char cmd[512] = {0};
    char *subdir = (char *) (dname);


    MYLOGD("bname : %s",bname);//    //md5name
    char md5Name[256] = {0};
    if(strlen(name) > 100){
        uint8_t result[16];
//        md5((uint8_t *)name,strlen(name),result);
        for (int i = 0; i < 16; i++){
            char tmpChar[3];
            sprintf(tmpChar,"%02x", result[i]);
            memcpy(&md5Name[i*2],tmpChar,2);
        }
       bname = md5Name;
       subdir = "";
    }



    sprintf(mypath, "%s/%s/%s",DUMP_LUA_DIR_PATH,"xLua", subdir);
    sprintf(cmd, "mkdir -p %s", mypath);
    system(cmd);
    MYLOGD("new_luaL_loadbuffer  bname:%s ",bname);

    MYLOGD("new_luaL_loadbuffer  subdir:%s",subdir);

    MYLOGD("new_luaL_loadbuffer mypath:%s ",mypath);

    int len=strlen(mypath);
    if(mypath[len-1]!='/')
    {
        sprintf(dstpath, "%s/%s", mypath, bname);
    } else {
        sprintf(dstpath, "%s/%s", mypath, bname);
    }

    if(is_load_dump_lua>=0)
    {
        struct stat st;

        if(stat(dstpath,&st)>=0&&st.st_size>0) {
            FILE *file = fopen(dstpath, "r");
            if (file != NULL) {
                fseek(file, 0, SEEK_END);
                size_t new_size = ftell(file);
                fseek(file, 0, SEEK_SET);
                char *new_buff = (char *) alloca(new_size + 1);
                fread(new_buff, new_size, 1, file);
                fclose(file);
                MYLOGD("new_luaL_loadbuffer=>load_dump_lua from path:%s",dstpath);
                return old_xluaL_loadbuffer(L,new_buff,new_size,name,mode);
            }
        }
    }
    int ret = old_xluaL_loadbuffer(L,buff,sz,name,mode);
    if(is_dump_lua>=0) {
        struct stat st;
        bool is_need_write=true;
        if(stat(dstpath,&st)>=0&&st.st_size>0) {
            is_need_write= false;
        }
        if(true||is_need_write)
        {
            int fd = open(dstpath, O_CREAT | O_RDWR);
            if (fd > 0) {
                int ret = write(fd, buff, sz);
                MYLOGD("new_luaL_loadbuffer fopen fwrite ret:%d path:%s", ret,dstpath);
                close(fd);
            } else {
                MYLOGD("new_luaL_loadbuffer fopen err:%s dstpath:%s", strerror(errno), dstpath);
            }
        }
    }
    return ret;
}
```
开始跑adb shell 链接，dump下来的代码文件就放在了
```
adb shell 
/data/media/0/mydump/lua/newsdata/module
```

```
adb pull /data/media/0/mydump/lua
```
parkourking 里面lua脚本加密****留疑（使用什么方法加密）****。使用python脚本解密lua脚本。
```
修改parkourkingplayerinfo.info
18 行 roleskinid=20
```
踩的小坑就是jj发现程序崩了会有守护进程，不能再起。所以需要结束程序，神奇的是ps ，kill以后并没有成功杀掉，ps发现又起了。但是在手机端结束程序是可以的(android 手机 结束应用的机制)，怀疑还有其他的进程再守护。


改完崩了 ，没有备份 炸裂。重新得到lua脚本。并备份为副本。要写出测试用例要对代码有个系统的认证，每个部分负责什么功能。

不晓得cocos 就是这种模式，还是游戏开发使用MVC架构.
# 测试
## 测试目的
默认客户端是绝对危险的，hacker 可以任意控制代码发送数据给服务器。测试通过修改发送来检查是否能够欺骗服务器，或者使服务器崩溃
## 修改日志
```
/parkourking/model/BaseObject3D.lua
BaseObject3D.setSize3D = function (self, width, height, length)
	self.boundingBox_:setSize3D(width, height, length)

	return 
end

==>
BaseObject3D.setSize3D = function (self, width, height, length)
	self.boundingBox_:setSize3D(2*width, 2*height, 2*length)

	return 
end
```
讲道理改了运行不了，就很难受。。。。
修改/parkourking/util/Log.lua
```
local IS_DEBUG = false
local IS_FILE = false

==>

local IS_DEBUG = true
local IS_FILE = true

```
完了一把，在android studio 筛选到JJLog-Lua ， 捕捉到一些信息
```
-- 排名信息 排位赛第三
MatchMsgType.REST_ACK  = {
        3, //猜测这是名词
        1 = 3, 
        32,
        2 = 32,
        0,
        0,
        gameMsg_ = false,
        match_ack_msg = {
            matchid = 3722400308,
            rest_ack_msg = {
                awardtimespan = 0,
                coin = 0,
                exchangerate = 0,
                gameresult = 0,
                gamescount = 0,
                hematiniccount = 4,
                hematiniclist = {
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                },
                lasthandscore = 0,
                life = 1500,
                multi = 0,
                nextawardleftsecond = 0,
                nextlevelgames = 0,
                nextlevelmulti = 0
                
                
-- 排名信息 排位赛第1 ，数据中除了matchid 不同以外没有其它不同 (后期展开测试修改matchid)
2019-11-14 10:23:04.151 7915-7998/cn.jj D/JJLog-Lua: [11:14:10:23: 4:151] [Log][ParkourKingPlaySceneController]	MatchMsgType.REST_ACK  = {
        3,
        1 = 3,
        32,
        2 = 32,
        0,
        0,
        gameMsg_ = false,
        match_ack_msg = {
            matchid = 402051416,
            rest_ack_msg = {
                awardtimespan = 0,
                coin = 0,
                exchangerate = 0,
                gameresult = 0,
                gamescount = 0,
                hematiniccount = 4,
                hematiniclist = {
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                    {
                        blood = 0,
                        cost = 0,
                    },
                },
                lasthandscore = 0,
                life = 1500,
                multi = 0,
                nextawardleftsecond = 0,
                nextlevelgames = 0,
                nextlevelmulti = 0,

                
-- 道具信息
2019-11-13 20:52:48.402 30458-30521/cn.jj D/JJLog-Lua: [11:13:20:52:48:402] [Log][PropSkillButton]	setSkill	302


-- 不知名神奇的信息
 [Log][BaseGameData]	state change	PLAY	=>	FINISH
[Log][CameraLayer]	onGameStateChange() gameState=	5	, lastGameState=	4
[Log][MatchPlayView]	onGameStateChange() gameState=	5	, lastGameState=	4

-- 怀疑是被道具攻击时字段
2019-11-14 11:13:45.242 7915-7998/cn.jj D/JJLog-Lua: [11:14:11:13:45:242] [Log][SoundManager]	playVoice() error, play fail, eventName=	skill_to_me_01

--  第一名玩家到达终点线(猜测提前发送该信息可以提前结束游戏 ==> 引发一个问题 如果只是客户端收到这个消息的话那就对远程服务器没有什么影响 ==> 区分是发包还是收包)
2019-11-14 11:15:02.439 7915-7998/cn.jj D/JJLog-Lua: [11:14:11:15: 2:439] [Log][BaseGameData]	state change	PLAY	=>	FINISH

--  玩道具赛抓到的log
019-11-14 12:00:59.165 7915-7998/cn.jj D/JJLog-Lua: [11:14:12:00:59:165] [Log][RobotComponent]	BOTERROR, no open node
2019-11-14 12:00:59.252 7915-7998/cn.jj D/JJLog-Lua: [11:14:12:00:59:252] [Log][PropSkillButton]	setSkill	306


```
发现一个好东西。
/parkourking/data/player/Player.lua
```
local RoleDef = require("parkourking.def.RoleDef")


local SUPER_JUMP_ANIMS = {
	[RoleDef.ID.WANGXIAOSHUAI] = {
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.DUFEIFEI] = {
		RoleDef.ANIM_NAME.JUMP1
	},
	[RoleDef.ID.AIDA] = {
		RoleDef.ANIM_NAME.JUMP1,
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.KELAODE] = {
		RoleDef.ANIM_NAME.JUMP1,
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.LONGYUE] = {  -- 这个名字不对。。。
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.ZHAOMANMAN] = { -- 这个名字也不对。。
		RoleDef.ANIM_NAME.JUMP1,
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.LILIKA] = {
		RoleDef.ANIM_NAME.JUMP1,
		RoleDef.ANIM_NAME.JUMP2
	},
	[RoleDef.ID.FUBAO] = {
		RoleDef.ANIM_NAME.JUMP1
	}
}
```
欸 在角色选择上有对应的角色整片代码细看是不可能细看的了，通过函数名称来大致猜测函数功能
看了一堆看不懂的 ，终于看到能看懂的了,明显对状态的检查。
```
Player.isJump = function (self)
	return self.curState_:getStateId() == PlayerDef.STATE_ID.JUMP
end
Player.isSlide = function (self)
	return self.curState_:getStateId() == PlayerDef.STATE_ID.SLIDE
end
Player.isLeft = function (self)
	return self.curState_:getStateId() == PlayerDef.STATE_ID.SHIFT_LEFT
end
Player.isRight = function (self)
	return self.curState_:getStateId() == PlayerDef.STATE_ID.SHIFT_RIGHT
end

Player.checkMinusSpeedTreasureTrigger = function (self)
	if self.isMatchMode(self) and (self.isSelf_ or self.isSelfCtrlAI_) then
		local equipTreasure = self.equipTreasureMap_[TreasureDef.ID.FENGRAOHAOJIAO]

		if equipTreasure then
			local isTriggered = math.random(1, 100) < equipTreasure.effectValue

			if isTriggered then
				self.buffCom_:addBuf(BuffDef.ID.MAGNET)
			end
		end
	end

	return 
end
Player.getMovement = function (self)
	return self.movement_
end
Player.getCollideCom = function (self)
	return self.collideCom_
end
Player.getMoveCom = function (self)
	return self.moveCom_
end
Player.getInputCom = function (self)
	return self.inputCom_
end
Player.getSkillCom = function (self)
	return self.skillCom_
end
Player.getBuffCom = function (self)
	return self.buffCom_
end
Player.getSpeedFieldCom = function (self)
	return self.speedFieldCom_
end
Player.getRobotCom = function (self)
	return self.robotCom_
end
Player.getAnimNames = function (self)
	return self.animNames_
end
Player.isTransparent = function (self)
	return self.isTransparent_
end
Player.setTransparent = function (self, isTransparent)
	self.isTransparent_ = isTransparent

	return 
end

Player.sleep = function (self)
	self.isSleep_ = true

	self.skillCom_:reset()
	self.buffCom_:reset()
	self.speedFieldCom_:reset()

	if self.moveCom_:isFootOnGround() or self.moveCom_:isFootOnObstacle() then
		self.changeState(self, PlayerDef.STATE_ID.IDLE)
	else
		self.changeState(self, PlayerDef.STATE_ID.FALL)
	end

	return 
end
Player.die = function (self)
	self.changeState(self, PlayerDef.STATE_ID.IDLE)

	local animNames = {
		RoleDef.ANIM_NAME.DEAD1
	}

	self.playAnim(self, {
		animNames[math.random(1, #animNames)]
	})
	self.buffCom_:reset()
	EventManager:addEvent(EventDef.ID.PLAYER_STATE_CHANGE, {
		userId = self.userId_,
		playerState = Player.STATE.DEAD
	})

	return 
end
Player.hit = function (self)
	self.skillCom_:hit()
	self.buffCom_:hit()
	self.robotCom_:hit()

	return 
end
Player.dizz = function (self)
	self.skillCom_:hit()
	self.buffCom_:dizz()
	self.robotCom_:hit()

	return 
end
Player.hitDestoryObstacle = function (self, obstacleId, isFlash, isPropObs)
	local obstacle = self.gameData_:getTrackManager():getObject(obstacleId)

	if obstacle then
		if not isPropObs then
			self.gameData_:getTrackManager():delObjectsByLength(obstacle.getFront(obstacle), obstacle.getLength(obstacle), obstacle.getX(obstacle))
		end

		self.gameData_:getTrackManager():delObject(obstacleId)
		EventManager:addEvent(EventDef.ID.TRACK_CLEAR, {
			delObjectIds = {
				obstacleId
			},
			isFlashAnim = isFlash and self.isSelf_,
			isPropObs = isPropObs or false
		})
	end

	return 
end
```

插入一行代码
```
Player.collideSuperJump = function (self)
	self.changeState(self, PlayerDef.STATE_ID.JUMP, true)
	log.e("Pareto: Hello World/n")
	return 
end
```
这里分析目的是想要了解角色操作的控制。

问了学长主要是完成协议上的漏洞。角色重定位，负责的任务就是随意修改发送的协议来达成服务器，或者客户端异常。
### 理解协议内容
/pb/ParkourkingMsg.lua
```
ParkourKingMsg.sendReportCollideReq = function (self, params)
	_sendReq("report_collide_req_msg", {
		user_id = params.userId, ==> user_id = 999,
		report_user_id = params.reportUserId,
		obstacle_id = params.obstacleId,
		collide_type = params.collideType,
		track_id = params.trackId,
		movement = params.movement
	})

	return 
end
```

缺乏了一点大型代码阅读经验，代码局部阅读回溯能力有限。
这次代码从游戏协议入手

找到一个游戏发包函数 ==> 分析包的作用 ，在那些地方调用了这个函数 ==> 猜测服务器对包的检验

/pb/ParkourKingMsg.lua
```
ParkourKingMsg.sendReportCollideReq = function (self, params)
	_sendReq("report_collide_req_msg", {
		user_id = params.userId,
		report_user_id = params.reportUserId,
		obstacle_id = params.obstacleId,
		collide_type = params.collideType,
		track_id = params.trackId,
		movement = params.movement
	})

	return 
end
```
/parkourking/data/player/compoent/CollideComponent.lua中，checkCollideObstacles 调用了这个函数，怀疑里面涉及到碰撞检测
```
49 :
--if isCheckSafePass and not self.player_:isSafePassObstacleId(obstacleId) and CollideDef.TYPE.PILLAR <= collideType and collideType <= CollideDef.TYPE.ROADBLOCK and playerBoundingBox.getFront(playerBoundingBox) < obstacle.getBack(obstacle) then
if self.player_:isSafePassObstacleId(obstacleId) then
```


```
log.e(TAG,"123")
解决了log 问题
```

目前想法能不能实现穿墙等 ， 外挂操作。
```
CollideComponent.checkCollideObstacles = function (self, obstacles)
	if DebugUtil:getCheatConfig().isControlCollide then
		return 
	end

	local isCollide = false
    
	if obstacles and 0 < #obstacles then
		local playerBoundingBox = self.player_:getBoundingBox()
		local isCheckSafePass = self.player_:isMatchMode() and self.player_:isSelf()
		local userId = self.player_:getUserId()
		local movement = self.player_:getMovement()

		for i = 1, #obstacles, 1 do
			local obstacle = obstacles[i]
			local obstacleId = obstacle.getId(obstacle)
			local collideType = obstacle.getCollideType(obstacle)

			if not self.player_:alreadyHit(obstacleId) then
				local result, overlapX, overlapY, overlapZ = obstacle.checkCollide(obstacle, playerBoundingBox, self.player_:getUserId())

				if result == CollideDef.RESULT.BANANA then
					_handleCollideObstacleBanana(self, obstacle)
				elseif result == CollideDef.RESULT.STUN_MINE then
					_handleCollideObstacleStunMine(self, obstacle)
				end

				if isCheckSafePass and not self.player_:isSafePassObstacleId(obstacleId) and CollideDef.TYPE.PILLAR <= collideType and collideType <= CollideDef.TYPE.ROADBLOCK and playerBoundingBox.getFront(playerBoundingBox) < obstacle.getBack(obstacle) then
					local safePassType = CollideDef.SAFE_PASS_TYPE.NONE

					if playerBoundingBox.getRight(playerBoundingBox) <= obstacle.getLeft(obstacle) then
						safePassType = CollideDef.SAFE_PASS_TYPE.LEFT
					elseif obstacle.getRight(obstacle) <= playerBoundingBox.getLeft(playerBoundingBox) then
						safePassType = CollideDef.SAFE_PASS_TYPE.RIGHT
					elseif obstacle.getTop(obstacle) <= playerBoundingBox.getBottom(playerBoundingBox) then
						safePassType = CollideDef.SAFE_PASS_TYPE.UP
					elseif playerBoundingBox.getTop(playerBoundingBox) <= obstacle.getBottom(obstacle) then
						safePassType = CollideDef.SAFE_PASS_TYPE.DOWN
					else
						safePassType = CollideDef.SAFE_PASS_TYPE.INSIDE
					end

					ParkourKingMsg:sendSafePassObstacleReq(userId, obstacleId, safePassType, movement)
					self.player_:saveSafePassObstacleId(obstacleId)
				end
			end
		end

		for i = 1, #obstacles, 1 do
			local obstacle = obstacles[i]

			if not self.player_:alreadyHit(obstacle.getId(obstacle)) then
				local result, overlapX, overlapY, overlapZ = obstacle.checkCollide(obstacle, playerBoundingBox, self.player_:getUserId())

				if result == CollideDef.RESULT.HIT then
					_handleCollideObstacleHit(self, obstacle)
				elseif result == CollideDef.RESULT.STEP then
					_handleCollideObstacleStep(self, obstacle, overlapY)
				elseif result == CollideDef.RESULT.STEP_EDGE then
					_handleCollideObstacleStepEdge(self, obstacle, overlapY)
				elseif result == CollideDef.RESULT.REBOUND_TO_LEFT then
					_handleCollideObstacleReboundToLeft(self, obstacle, overlapX)
				elseif result == CollideDef.RESULT.REBOUND_TO_RIGHT then
					_handleCollideObstacleReboundToRight(self, obstacle, overlapX)
				elseif result == CollideDef.RESULT.UP_SPRING then
					_handleCollideObstacleUpSpring(self, obstacle)
				end

				if result ~= CollideDef.RESULT.NONE then
					isCollide = true

					break
				end
			end
		end
	end

	if not isCollide and self.player_:getMoveCom():isFootOnObstacle() then
		self.player_:getMoveCom():setFootOnObstacle(false)
	end

	return 
end
```
```
	Log.e("CollideProps id + ",obstacles)
``` 
将障碍物id 打印出来对照

重点关注
```
obstacle.checkCollide()
```