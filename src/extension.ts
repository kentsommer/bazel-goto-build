import * as vscode from 'vscode';
import { exec } from 'child_process';
import path = require("path");

const execGoToBuild = (filepath: string) =>
    new Promise<string>((resolve, reject) => {
		let wd = path.dirname(filepath);
		let toolPath = path.join(process.cwd(), './src/goto_build.py');
		let cmd: string = toolPath + " -i " + filepath;
        exec(cmd, {cwd: wd}, (err, out) => {
            if (err) {
				console.log(err);
                return reject(err);
            }
            return resolve(out);
        });
});

export function activate(context: vscode.ExtensionContext) {

	console.log('"bazel-goto-build" is now active!');

	let disposable = vscode.commands.registerCommand('bazel-goto-build.goToBuild', async () => {
		var activeTextEditor = vscode.window.activeTextEditor;
		if (activeTextEditor) {
			// Get full filepath.
			var currentlyOpenTabfilePath = activeTextEditor.document.fileName;
			// Run our bazel-goto-build tool to get the BUILD file and line of containing target
			// for the given source file.
			const buildAndLine = await execGoToBuild(currentlyOpenTabfilePath);
			const buildANdLineSplit = buildAndLine.split(":");
			const buildPath = buildANdLineSplit[0];
			const lineToGo: number = parseInt(buildANdLineSplit[1]);
			vscode.workspace.openTextDocument(buildPath)
            .then(document =>
				vscode.window.showTextDocument(document)).then(() => {
					let activeEditor = vscode.window.activeTextEditor;
					if (activeEditor) {
						let range = activeEditor.document.lineAt(lineToGo -1).range;
						activeEditor.selection =  new vscode.Selection(range.start, range.end);
						activeEditor.revealRange(range);
					}
				}
			);
		}
	});
	context.subscriptions.push(disposable);
}

export function deactivate() {}