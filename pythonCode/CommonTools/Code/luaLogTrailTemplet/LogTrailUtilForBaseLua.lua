LogUtil = {}
function LogUtil:new(o_)
    o_ = o_ or {}
    setmetatable(o_, self)
    self.__index = self
    self.functionStack = {}
    -- 给一个容错空间
    table.insert(self.functionStack, "Main")
    self.interStr = "|   "
    self.passCount = 0
    return o_
end

function LogUtil:getInstance()
    if self._instance == nil then
        self._instance = self:new()
    end
    return self._instance
end

function LogUtil:serialize(obj_)
    local _lua = ""
    local _type = type(obj_)
    if _type == "number" then
        _lua = _lua .. obj_
    elseif _type == "boolean" then
        _lua = _lua .. tostring(obj_)
    elseif _type == "string" then
        _lua = _lua .. string.format("%q", obj_)
    elseif _type == "table" then
        _lua = _lua .. "{"
        for _k, _v in pairs(obj_) do
            _lua = _lua .. "[" .. self:serialize(_k) .. "]=" .. self:serialize(_v) .. ","
        end
        local metatable = getmetatable(obj_)
        if metatable ~= nil and type(metatable.__index) == "table" then
            for _k, _v in pairs(metatable.__index) do
                _lua = _lua .. "[" .. self:serialize(_k) .. "]=" .. self:serialize(_v) .. ","
            end
        end
        _lua = _lua .. "}"
    elseif _type == "nil" then
        return nil
    else
        error("can not serialize a " .. _type .. " type.")
    end
    return _lua
end

function LogUtil:unserialize(lua_)
    local _type = type(lua_)
    if _type == "nil" or lua_ == "" then
        return nil
    elseif _type == "number" or _type == "string" or _type == "boolean" then
        lua_ = tostring(lua_)
    else
        error("can not unserialize a " .. _type .. " type.")
    end
    lua_ = "return " .. lua_
    local _func = loadstring(lua_)
    if _func == nil then
        return nil
    end
    return _func()
end

-- 输出 字符串、数字、boolean、空值 ，其他过滤
function LogUtil:getTableStr(table_,level_)
    -- 不能一直递归下去，所以就解释几个层级，否者容易堆栈溢出
    if level_<=0 then
        return nil
    end
    local _tableStr = ""
    local _parList = {}
    for _key, _value in pairs(table_) do
        if type(_value) == "string" or type(_value) == "number" or type(_value) == "boolean" or _value == nil then
            table.insert(_parList, _key .. ":" .. tostring(_value))
        elseif type(_value)=="table" then
            local _nextLevelTable =  self:getTableStr(_value,level_-1)
            if _nextLevelTable then
                table.insert(_parList, _key .. ":" .._nextLevelTable)
            end
        end
    end
    _tableStr = "{"
    for i=1 , #_parList do
        _tableStr = _tableStr .._parList[i]
        if i ~= #_parList then
            _tableStr = _tableStr ..","
        end
    end
    _tableStr = _tableStr .."}"
    return _tableStr
end

function LogUtil:parCut(par_)
    local _par = tostring(par_)
    local _start, _len = string.find(_par, 'table: 0x')
    if _start == 1 then
        _par = self:getTableStr(par_,2)
    else
        _start, _len = string.find(_par, 'function: 0x')
        if _start == 1 then
            _par = "func"
        else
            _start, _len = string.find(_par, 'userdata: 0x')
            if _start == 1 then
                _par = "userdata"
            end
        end
    end

    local _maxLen = 100
    local _cutLen = _maxLen
    if string.len(_par) > _maxLen then
        _cutLen = _maxLen - 3
    end
    local _backStr = string.sub(_par, 1, _cutLen)
    if (_cutLen ~= _maxLen) then
        _backStr = _backStr .. "..."
    end
    return _backStr
end

function LogUtil:fi(path_, functionName_, comment_, pass_, par_)
    local _nowFunStr = path_ .. " -> " .. functionName_
    if pass_ == true then
        self.passCount = self.passCount + 1
    end

    if self.passCount > 0 then
        -- 当前已经被锁
        return
    elseif self.passCount == 0 then
        -- 记录这个方法执行时的相关信息
        local _tempTable = {}
        -- 组合成唯一函数路径
        table.insert(self.functionStack, _nowFunStr)

        -- 层级字符串
        local _tempStr = ""
        for i = 1, #self.functionStack do
            _tempStr = _tempStr .. self.interStr
        end

        -- 层级叠加得到当前的方法执行字符串
        _tempStr = _tempStr .. _nowFunStr

        -- 显示LOG
        if comment_ == nil then
            comment_ = ""
        end
        print("Λ" .. _tempStr .. "  =>  " .. par_)
    else
        print "ERROR -------------------------------passCount - fi "
    end
end

function LogUtil:fo(path_, functionName_, comment_, pass_, par_)
    -- 当前的路径
    local _nowFunStr = path_ .. " -> " .. functionName_

    if #self.functionStack == 0 then
        print("ERROR 意外的函数堆栈为空")
        return
    end

    if self.passCount > 0 then

    elseif self.passCount == 0 then
        -- 可以输出LOG的情况下
        -- pass_ 本身需要跳过
        if pass_ then
            return
        end

        local _tempStr = ""
        for i = 1, #self.functionStack do
            _tempStr = _tempStr .. self.interStr
        end

        -- 获取堆栈的最后一个 -- 不论后面对不对,都推出最后一个
        local _lastFunStr = table.remove(self.functionStack, #self.functionStack)

        -- 组合成唯一函数路径，进出应当是一一对应的，如果没对应上就出错了
        if _nowFunStr == _lastFunStr then
            _tempStr = _tempStr .. _lastFunStr  -- 显示LOG
            if comment_ == nil then
                comment_ = ""
            end

            if par_ then
                print("V" .. _tempStr .. "  <=  " .. par_)
            else
                print("V" .. _tempStr .. "  <=  ")
            end
        else
            print "ERROR -------------------------------------------------------"
            print("now  检查这个函数的写法，有逻辑没有闭合 : " .. _nowFunStr)
            print("last : " .. _lastFunStr)
        end
    else
        print "ERROR -------------------------------passCount - fo "
    end

    -- 已经锁的情况下解锁 -- 解锁
    if pass_ == true then
        self.passCount = self.passCount - 1
    end
end
return LogUtil