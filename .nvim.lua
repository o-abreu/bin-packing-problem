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

-- The profile's `python3` is a bare interpreter (no pandas/matplotlib) and the
-- jupyter kernelspec Quarto picks runs plain `python` from PATH, so
-- `:QuartoPreview` died on the report's plotting chunks. Point PATH, VIRTUAL_ENV
-- and QUARTO_PYTHON at the project's venv (also used by the code runner).
local venv = root .. '/.devenv/state/venv'
if vim.fn.isdirectory(venv .. '/bin') == 1 then
  local venv_bin = venv .. '/bin'
  if not (vim.env.PATH or ''):find(venv_bin, 1, true) then
    vim.env.PATH = venv_bin .. ':' .. vim.env.PATH
  end
  vim.env.VIRTUAL_ENV = venv
  vim.env.QUARTO_PYTHON = venv_bin .. '/python'
end
