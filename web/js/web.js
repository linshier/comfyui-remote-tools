import { app } from "/scripts/app.js"

app.registerExtension({
    name: "LoadBase64(js)",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "LoadBase64(js)") {
            const orig_nodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                orig_nodeCreated?.apply(this, arguments);
                
                let base64Widget = this.widgets.filter(w => w.name == "base64")[0]
                base64Widget.type = "hidden";
                
                const fileInput = document.createElement("input");
                Object.assign(fileInput, {
                    type: "file",
                    accept: "image/jpeg,image/png,image/webp",
                    style: "display: none",
                    multiple: true,
                    onchange: async () => {
                        let base64 = [];
                        this.imgs = [];
                        for (let i = 0; i < fileInput.files.length; i++) {
                            const reader = new FileReader();
                            reader.onload = async event => {
                                let data = event.target.result;
                                base64.push(data);
                                base64Widget.value = JSON.stringify(base64);
                                // previews
                                let image = new Image()
                                image.onload = () => {
                                    this.imgs.push(image);
                                    this.setSizeForImage?.();
                                    app.graph.setDirtyCanvas(true, true);
                                };
                                image.src = data;
                            }
                            reader.readAsDataURL(fileInput.files[i]);
                        }
                    },
                });
                document.body.append(fileInput);

                let uploadWidget = this.addWidget(
                    "button",
                    "choose images to upload",
                    "",
                    () => {
                        app.canvas.node_widget = null;
                        fileInput.click();
                    }
                );
                uploadWidget.options.serialize = false;

                let clearWidget = this.addWidget(
                    "button",
                    "clear",
                    "",
                    () => {
                        app.canvas.node_widget = null;
                        base64Widget.value = "[]"
                        fileInput.value = "";
                        this.imgs = null;
                    }
                );
                clearWidget.options.serialize = false;

                const onRemoved = this.onRemoved;
                this.onRemoved = function () {
                    onRemoved?.apply(this, arguments);
                };
            };
        }
    }
});