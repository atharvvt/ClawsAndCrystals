function initRazorpayPayment(config) {
    var button = document.getElementById("rzp-button");
    var form = document.getElementById("payment-verify-form");

    if (!button || !form) {
        return;
    }

    var options = {
        key: config.key,
        amount: config.amount,
        currency: "INR",
        name: "Claws & Crystals",
        description: "Order Payment",
        order_id: config.orderId,
        prefill: config.prefill,
        theme: {
            color: "#C9A84C",
        },
        handler: function (response) {
            document.getElementById("razorpay_payment_id").value =
                response.razorpay_payment_id;
            document.getElementById("razorpay_order_id").value =
                response.razorpay_order_id;
            document.getElementById("razorpay_signature").value =
                response.razorpay_signature;
            form.submit();
        },
        modal: {
            ondismiss: function () {
                alert("Payment was cancelled. You can try again when ready.");
            },
        },
    };

    var rzp = new Razorpay(options);

    button.addEventListener("click", function () {
        rzp.open();
    });
}
