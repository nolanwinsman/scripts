--- This is a script to rename all 110 episodes of Legend of the Galactic Heroes to the proper plex naming convention
--- @Author Nolan Winsman
--- @Date 2025-06-20

function Pad_three(num)
	return string.format("%03d", num)
end

local seasons = { 26, 28, 32, 24 }

io.write("Directory of LOGH: ")
local d = io.read()

for k, v in ipairs(seasons) do
	print(k, v)
end

local totalepisodeCount = 1
local episodeCount = 1
local seasonCount = 1
for dir in io.popen('dir "' .. d .. '" /b'):lines() do
	if string.match(dir, totalepisodeCount) then
		print("ep: " .. episodeCount .. " S " .. seasonCount .. " Total: " .. totalepisodeCount)
		local newName = "Legend of the Galactic Heroes S0" .. seasonCount .. "E" .. Pad_three(episodeCount) .. ".mkv"

		print("Renaming " .. dir .. " To: " .. newName .. "")
		local oldPath = d .. "\\" .. dir
		local newPath = d .. "\\" .. newName
		local ok, err = os.rename(oldPath, newPath)
		if not ok then
			print("Failed to rename: " .. err)
		end

		if episodeCount == seasons[seasonCount] then
			episodeCount = 1
			seasonCount = seasonCount + 1
		else
			episodeCount = episodeCount + 1
		end
		totalepisodeCount = totalepisodeCount + 1
	end
end
