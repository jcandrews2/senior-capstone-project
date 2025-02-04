import React, { useState } from "react";
import ReactDOM from "react-dom";
import { IoMdClose } from "react-icons/io";

const DisputeModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      <button className="m-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold">
        Dispute
      </button>
      {isOpen &&
        ReactDOM.createPortal(
          <div className="">
            <div className="">
              <button
                className="m-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
                onClick={toggleModal}
              >
                <IoMdClose />
              </button>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
};

export default DisputeModal;
