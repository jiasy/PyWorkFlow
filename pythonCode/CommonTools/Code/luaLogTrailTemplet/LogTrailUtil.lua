
local logTrailUtil = class("logTrailUtil")
function logTrailUtil:ctor(params_)
	self.functionStack = []
	self.interStr = "|   "
	self.passCount = 0
end

function logTrailUtil:fi(path_, functionName_, comment_, pass_, par_)
    if pass_ == true then
        self.passCount = self.passCount + 1
    end

    if self.passCount > 0 then
        -- 当前已经被锁
        return
    elseif self.passCount == 0 then
        -- 记录这个方法执行时的相关信息
        _tempTable = {}
        -- 组合成唯一函数路径
        _tempTable["uniquePath"] = path_.." -> "..functionName_
        table.insert(self.functionStack,_tempTable)

        -- 层级字符串
        _tempStr = ""
        for i=1 , #self.functionStack do
			_tempStr = _tempStr .. self.interStr
		end 

        -- 层级叠加得到当前的方法执行字符串
        _tempStr = _tempStr .. path_ .. " -> " .. functionName_

        -- 显示LOG
        if comment_ == nil then
        	comment_ = ""
        end

        print "->" .. _tempStr .. "  :  " .. comment_ .. " " .. par_
    else
        print "ERROR -------------------------------passCount - fi "
    end
end

function logTrailUtil:fo(path_, funcName_, comment_, pass_, par_)
        -- 当前的路径
        _nowFunStr = path_ .. " -> " .. functionName_

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

            _tempStr = ""
            for i=1 , #self.functionStack do
				_tempStr = _tempStr..interStr
			end 

            -- 获取堆栈的最后一个 -- 不论后面对不对,都推出最后一个
            _tempTable = table.remove(self.functionStack , #self.functionStack)

            -- 最后一个Function组合名
            _lastFunStr = _tempTable["uniquePath"]

            -- 组合成唯一函数路径，进出应当是一一对应的，如果没对应上就出错了
            if _nowFunStr == _lastFunStr then
                _tempStr = _tempStr .. _lastFunStr  -- 显示LOG
                if comment_ == nil then
                	comment_ = ""
                end

                if par_ then
                	print "<-" .. _tempStr .. "  :  " .. comment_ + " " .. par_
                else
                	print "<-" .. _tempStr .. "  :  " .. comment_ 
                end
            else
                print "ERROR -------------------------------"
                print "now  : " .. _nowFunStr
                print "last : " .. _lastFunStr
            end
        else
        	print "ERROR -------------------------------passCount - fo "
        end

        -- 已经锁的情况下解锁 -- 解锁
        if pass_ == true then
            self.passCount = self.passCount - 1
        end
end

cc.exports.LogUtil={}
function LogUtil:getInstance()
    if self.instance == nil then
        self.instance = logTrailUtil:new()
    end
    return self.instance
end