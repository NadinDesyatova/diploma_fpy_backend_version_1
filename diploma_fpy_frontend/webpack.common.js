import path from "path";
import { fileURLToPath } from 'url';
import HtmlWebPackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import pkg from "mini-css-extract-plugin";
const { loader: _loader } = pkg;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


export const entry = './src/main.jsx';
export const output = {
  path: path.resolve(__dirname, 'static/diploma_frontend'),
  filename: 'main.js',
};
export const module = {
  rules: [
    {
      test: /\.js|jsx$/,
      exclude: /node_modules/,
      use: {
        loader: "babel-loader",
      },
    },
    {
      test: /\.html$/,
      use: [
        {
          loader: "html-loader",
        },
      ],
    },
    {
      test: /\.css$/,
      use: [_loader, "css-loader"],
    },

    {
      test: /\.(png|svg|jpg|jpeg|gif)$/i,
      type: "asset/resource",
    },
    {
      test: /\.(woff|woff2|eot|ttf|otf)$/i,
      type: "asset/resource",
    },
  ],
};

export const resolve = {
  extensions: ['.js', '.jsx'],
};

export const plugins = [
  new HtmlWebPackPlugin({
    template: "./index.html",
    filename: "./index.html",
  }),
  new MiniCssExtractPlugin({
    filename: "[name].css",
    chunkFilename: "[id].css",
  }),
];
