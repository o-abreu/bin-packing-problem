-- Prefer this project's own Quarto/TeX (devenv profile) over any global one,
-- so `:QuartoPreview` uses the pinned Quarto 1.6.43 + TeX Live from the flake
-- instead of the profile's Quarto (which fails to find IEEEtran.cls).
vim.opt.exrc = true
local root = vim.fn.fnamemodify(debug.getinfo(1, 'S').source:sub(2), ':p:h')
local bin = root .. '/.devenv/profile/bin'
local path = vim.env.PATH or ''
if vim.fn.isdirectory(bin) == 1 and not path:find(bin, 1, true) then
  vim.env.PATH = bin .. ':' .. path
end
