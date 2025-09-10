import { merge } from "webpack-merge";
import * as common from "./webpack.common.js";
import CssMinimizerPlugin from "css-minimizer-webpack-plugin";

export default merge(common, {
  mode: "production",
  optimization: {
    minimizer: [new CssMinimizerPlugin()],
  },
});
