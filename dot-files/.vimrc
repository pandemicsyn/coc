" call pathogen#infect()
" call pathogen#helptags()

"if has("gui_running")
"colorscheme heroku
    "    colorscheme flat2
    syn keyword MyGroup mux
    " Then EITHER (define your own colour scheme):
 ""   hi MyGroup guifg=Blue ctermfg=Blue term=bold
    " " OR (make the colour scheme match an existing one):
    " hi link MyGroupName Todo
"else
"    colorscheme flat2
"endif
call pathogen#runtime_append_all_bundles()
let g:tagbar_type_go = {
    \ 'ctagstype' : 'go',
    \ 'kinds'     : [
        \ 'p:package',
        \ 'i:imports:1',
        \ 'c:constants',
        \ 'v:variables',
        \ 't:types',
        \ 'n:interfaces',
        \ 'w:fields',
        \ 'e:embedded',
        \ 'm:methods',
        \ 'r:constructor',
        \ 'f:functions'
    \ ],
    \ 'sro' : '.',
    \ 'kind2scope' : {
        \ 't' : 'ctype',
        \ 'n' : 'ntype'
    \ },
    \ 'scope2kind' : {
        \ 'ctype' : 't',
        \ 'ntype' : 'n'
    \ },
    \ 'ctagsbin'  : 'gotags',
    \ 'ctagsargs' : '-sort -silent'
    \ }
let g:airline_powerline_fonts = 1
let g:airline_theme = "kolor"
filetype off
" let g:neocomplcache_enable_at_startup = 1
" let g:neocomplete#enable_at_startup = 1
set nocompatible
filetype plugin indent on
syntax on
set noshowmode
syntax on
set vb
set ai ts=4 tw=0 sw=4 expandtab
set hlsearch
" set paste
set title
filetype plugin on
filetype plugin indent on
" Increase indentation after open-braces and match close-brace indentation to
" their open-brace indentations.
set smartindent
set backspace=indent,eol,start
" Automatically jump to where the search matches as it is being typed.
set incsearch
" Try to keep 4 extra lines of context at the top and bottom of the screen.
set scrolloff=4
" Turns on syntax highlighting.
syn enable
au BufRead,BufNewFile *.go set filetype=go
" Turn on mouse mode.
set mouse=a
set ttymouse=xterm2
" highlight lines over 79 cols, spaces at the end of lines and tab characters
highlight BadStyle ctermfg=yellow
match BadStyle "\(\%>79v.\+\|\t\| \+$\)"
autocmd FileType go setlocal noexpandtab shiftwidth=4 tabstop=4 softtabstop=4 nolist
" pep8
let g:pep8_map='<leader>8'
" fucking pyflakes highlighting
highlight SpellBad term=reverse ctermbg=1
""""""""""""""""""""""""""""""
" => Statusline
""""""""""""""""""""""""""""""
" Always hide the statusline
set laststatus=2

" Format the statusline
set statusline=\ %{HasPaste()}%F%m%r%h\ %w\ \ CWD:\ %r%{CurDir()}%h\ \ \ Line:\ %l/%L:%c


function! CurDir()
    let curdir = substitute(getcwd(), '/Users/fhines/', "~/", "g")
    return curdir
endfunction

function! HasPaste()
    if &paste
        return 'PASTE MODE  '
    else
        return ''
    endif
endfunction

autocmd FileType go setlocal noexpandtab shiftwidth=4 tabstop=4 softtabstop=4 nolist
" let g:go_fmt_command = "goimports"
let g:go_fmt_command = "goimports"

au FileType go nmap <Leader>gd <Plug>(go-doc)
au FileType go nmap <Leader>gv <Plug>(go-doc-vertical)
au FileType go nmap <Leader>gb <Plug>(go-doc-browser)
set number
au FileType go nmap <leader>r <Plug>(go-run)
au FileType go nmap <leader>b <Plug>(go-build)
au FileType go nmap <leader>t <Plug>(go-test)
au FileType go nmap <leader>c <Plug>(go-coverage)
let g:go_highlight_array_whitespace_error = 1
let g:go_highlight_chan_whitespace_error = 1
let g:go_highlight_extra_types = 1
let g:go_highlight_space_tab_error = 1
let g:go_highlight_trailing_whitespace_error = 1
let g:go_highlight_functions = 1
let g:go_highlight_methods = 1
let g:go_highlight_structs = 1
let g:go_highlight_operators = 1
let g:go_highlight_build_constraints = 1
let g:go_textobj_enabled = 1
colorscheme heroku
let g:rehash256 = 1
