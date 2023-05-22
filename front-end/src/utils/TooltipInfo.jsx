import { Tooltip } from "react-tippy";
import "react-tippy/dist/tippy.css";
import InfoIcon from "@mui/icons-material/Info";

export default function TooltipInfo() {
  return (
    <Tooltip
      title="when you try to download more than once, your browser will try to prevent you from downloading again. You can manually disable this option in the browser or reload the page."
      position="bottom"
      trigger="mouseenter"
    >
      <InfoIcon />
    </Tooltip>
  )
}
