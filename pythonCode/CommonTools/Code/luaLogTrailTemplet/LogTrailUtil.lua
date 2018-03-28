cc.exports.LogUtil = {}
function LogUtil:new(o_)
    o_ = o_ or {}
    setmetatable(o_, self)
    self.__index = self
    self.functionStack = {}
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

function LogUtil:parCut(par_)
    local _par = tostring(par_)

    local _start, _len = string.find(_par, 'table: 0x')
    if _start == 1 then
        _par = "table"
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
        _tempTable["uniquePath"] = path_ .. " -> " .. functionName_
        table.insert(self.functionStack, _tempTable)

        -- 层级字符串
        local _tempStr = ""
        for i = 1, #self.functionStack do
            _tempStr = _tempStr .. self.interStr
        end

        -- 层级叠加得到当前的方法执行字符串
        _tempStr = _tempStr .. path_ .. " -> " .. functionName_

        -- 显示LOG
        if comment_ == nil then
            comment_ = ""
        end
        -- print ("Λ" .. _tempStr .. "  :  " .. tostring(comment_) .. " " .. par_)
        print("Λ" .. _tempStr .. "  :  " .. par_)
    else
        print "ERROR -------------------------------passCount - fi "
    end
end

function LogUtil:fo(path_, functionName_, comment_, pass_, par_)
    -- 当前的路径
    local _nowFunStr = path_ .. " -> " .. functionName_

    if #self.functionStack == 0 then
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
        local _tempTable = table.remove(self.functionStack, #self.functionStack)

        -- 最后一个Function组合名
        local _lastFunStr = _tempTable["uniquePath"]

        -- 组合成唯一函数路径，进出应当是一一对应的，如果没对应上就出错了
        if _nowFunStr == _lastFunStr then
            _tempStr = _tempStr .. _lastFunStr  -- 显示LOG
            if comment_ == nil then
                comment_ = ""
            end

            if par_ then
                -- print ("V" .. _tempStr .. "  :  " .. tostring(comment_) + " " .. par_)
                print("V" .. _tempStr .. "  :  " .. par_)
            else
                -- print ("V" .. _tempStr .. "  :  " .. tostring(comment_))
                print("V" .. _tempStr .. "  :  ")
            end
        else
            print "ERROR -------------------------------"
            print("now  : " .. _nowFunStr)
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