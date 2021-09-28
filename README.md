# bazel-goto-build

Tool to enable jumping to the target containing the source file (relies on [buildozer](https://github.com/bazelbuild/buildtools))

## Features

VSCode:
* Provides a single command `bazel-goto-build.goToBuild` which will jump to the BUILD file and line at which the target is defined which contains the current source file.

Vim/NeoVim:
* Manual work is needed as there is not yet a plugin which integrates the tool. Please see the `Integration with Vim/NeoVim` section below.

## Requirements

This tool (both VSCode and Vim/NeoVim) currently only works on linux. It depends heavily on [buildozer](https://github.com/bazelbuild/buildtools) to parse BUILD files and fine the srcs, hdrs (if applicable), and data deps for each rule in a Bazel WORKSPACE. 

Support for Windows and OSX may be considered in the future.

The main driver script (`goto_build.py`) depends on [buildozer](https://github.com/bazelbuild/buildtools) but will fetch it itself the first time it is run.

## Integration with Vim/NeoVim

To use the tool in Vim/NeoVim, add the following to your `.vimrc` or `init.vim` and adjust the `command` so that the path points to the `goto_build.py` file in this repository.

```
function! s:gotobuild() abort
    let l:file_path=expand('%:p')
    let l:command="path/to/goto_build.py -i " . l:file_path
    let l:result=trim(system(l:command))
    if l:result == ""
      echo 'No corresponding BUILD file found'
    else
      let l:result_list=split(l:result, ':')
      let l:build_file_name=l:result_list[0]
      let l:build_file_line=l:result_list[1]
      execute 'edit +' . l:build_file_line l:build_file_name
      execute 'normal! zz'
    endif
endfunction
command! -complete=command GOTOBuild call <SID>gotobuild()
nnoremap <silent> mB :GOTOBuild<CR>
```
