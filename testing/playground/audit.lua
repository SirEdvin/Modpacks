-- Generated playground audit program.
-- Run with: audit

local REPORT = "/authored-peripherals.json"

local function sortedNames()
  local names = peripheral.getNames()
  table.sort(names)
  return names
end

local function snapshot()
  local report = {
    generatedAt = os.epoch("utc"),
    computerID = os.getComputerID(),
    peripherals = {},
  }

  for _, name in ipairs(sortedNames()) do
    report.peripherals[#report.peripherals + 1] = {
      name = name,
      types = { peripheral.getType(name) },
      methods = peripheral.getMethods(name),
    }
  end

  local handle = assert(fs.open(REPORT, "w"))
  handle.write(textutils.serializeJSON(report))
  handle.close()

  print(("Found %d attached peripherals"):format(#report.peripherals))
  for _, entry in ipairs(report.peripherals) do
    print(entry.name .. " -> " .. table.concat(entry.types, ", "))
  end
  print("Report: " .. REPORT)
  return report
end

return snapshot()
