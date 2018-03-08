如将card.plist card.png 进行拆分
脚本使用方法 ./unpacker.py card

注意：plist文件中的每个单个文件名不能存在路径，如
	<dict>
			<key>mj_0_0_1.png</key>
	</dict>

	不能是
	<dict>
			<key>a/b/c/mj_0_0_1.png</key>
	</dict>